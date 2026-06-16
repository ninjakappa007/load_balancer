import uvicorn
from fastapi import FastAPI, Request
from concurrent.futures import ThreadPoolExecutor


app = FastAPI()
SERVER_PORT_LIST = [8001, 8002, 8004]

@app.get('/{full_path:path}')
def read_root(request : Request, full_path: str):
    _, server_port = request.scope.get("server", (None, None))
    return {'message' : f'Hello! This response is dynamically generated from Backend Path : {full_path} and Port: {server_port} '}

def run_custom_server(port: int):
    print(f"Starting server on port {port}...")
    uvicorn.run(app, host="127.0.0.1", port=port, reload=False)


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=len(SERVER_PORT_LIST)) as executor:
        print(f'Starting server for port :: {SERVER_PORT_LIST}')
        list(executor.map(run_custom_server, SERVER_PORT_LIST))
