from fastapi import FastAPI, Request, Response
import httpx
import itertools
import asyncio

app = FastAPI()

SERVER_PORT_LIST = [8001, 8002, 8003, 8004]

healthy_servers = [
    f"http://0.0.0.0:{port}"
    for port in SERVER_PORT_LIST
]

backend_cycle = itertools.cycle(healthy_servers)

async_client = httpx.AsyncClient(
    timeout=3.0
)

# Protect shared state
lock = asyncio.Lock()


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy(request: Request, path: str):
    global backend_cycle

    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()
    params = dict(request.query_params)

    # Snapshot current number of healthy servers
    async with lock:
        attempts = len(healthy_servers)

    if attempts == 0:
        return Response(
            content="No healthy backends available",
            status_code=503
        )

    for _ in range(attempts):

        async with lock:
            if not healthy_servers:
                break

            backend_server = next(backend_cycle)

        backend_url = f"{backend_server}/{path}"

        try:
            backend_response = await async_client.request(
                method=request.method,
                url=backend_url,
                headers=headers,
                content=body,
                params=params,
                follow_redirects=False,
            )

            print(
                f"[LB] {request.method} /{path} "
                f"→ {backend_server} "
                f"({backend_response.status_code})"
            )

            response_headers = dict(backend_response.headers)

            # Remove hop-by-hop headers
            response_headers.pop("content-encoding", None)
            response_headers.pop("transfer-encoding", None)
            response_headers.pop("connection", None)

            return Response(
                content=backend_response.content,
                status_code=backend_response.status_code,
                headers=response_headers,
            )

        except (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
        ) as e:

            print(f"[LB] Backend failed: {backend_server} ({e})")

            async with lock:
                if backend_server in healthy_servers:
                    healthy_servers.remove(backend_server)

                    if healthy_servers:
                        backend_cycle = itertools.cycle(
                            healthy_servers
                        )

            # Try the next backend
            continue

    return Response(
        content="All backends are unavailable",
        status_code=503
    )


@app.get("/metrics")
async def metrics():
    async with lock:
        return {
            "healthy_backends": healthy_servers,
            "count": len(healthy_servers),
        }


@app.on_event("shutdown")
async def shutdown():
    await async_client.aclose()