import requests
from pydantic import json

response = requests.get('http://127.0.0.1:8000/')

response.raise_for_status()
print(f'Status code : {response.status_code}')
print(f'Body : {response.text}')