import subprocess
from concurrent.futures import ThreadPoolExecutor
import time

server_port_list = ['8001', '8002', '8003', '8004']

def start_http_server(server_port: str):
    subprocess.call(['python3', '-m', 'http.server', server_port])

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(start_http_server, server_port_list)
