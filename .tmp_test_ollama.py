import requests, json
url='http://127.0.0.1:11434/api/chat'
payload={
  'model':'tinyllama:latest',
  'messages':[{'role':'system','content':'You are a helpful assistant for smoke-testing.'},{'role':'user','content':'Say hello and confirm you are ready.'}],
  'stream': False
}
resp = requests.post(url, json=payload, timeout=60)
print('status', resp.status_code)
try:
    print(json.dumps(resp.json(), indent=2))
except Exception as e:
    print('raw:', resp.text)
