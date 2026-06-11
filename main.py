from fastapi import FastAPI, Request, Response
from start_servers import SERVER_PORT_LIST
import httpx
import itertools




app = FastAPI()

# round robin
backend_cycle = itertools.cycle([f'http://0.0.0.0:{str(port)}/' for port in SERVER_PORT_LIST])
async_client = httpx.AsyncClient()


@app.api_route("/",  methods=["GET", "POST", "PUT", "DELETE"])
async def read_root(request : Request):

    backend_url = next(backend_cycle)

    headers = dict(request.headers)
    body = await request.body()
    params = dict(request.query_params)

    backend_response = await async_client.request(
        method=request.method,
        url=backend_url,
        headers=headers,
        content=body,
        params=params,
        follow_redirects=False
    )

    return Response(
        content=backend_response.content,
        status_code=backend_response.status_code,
        headers=dict(backend_response.headers)
    )