import subprocess
from concurrent.futures import ThreadPoolExecutor
from http.server import HTTPServer, BaseHTTPRequestHandler

SERVER_PORT_LIST = [8001, 8002, 8003, 8004]


class CustomBackendHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        current_port = self.server.server_address[1]

        custom_message = f"Hello! This response is dynamically generated from Backend Port: {current_port}\n"
        response_bytes = custom_message.encode('utf-8')

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()

        self.wfile.write(response_bytes)

    def log_message(self, format, *args):
        pass


def run_custom_server(port: int):
    server = HTTPServer(("127.0.0.1", port), CustomBackendHandler) # type: ignore
    print(f"Backend worker successfully listening on port {port}...")
    server.serve_forever()



if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=len(SERVER_PORT_LIST)) as executor:
        print(f'Starting server for port :: {SERVER_PORT_LIST}')
        list(executor.map(run_custom_server, SERVER_PORT_LIST))
