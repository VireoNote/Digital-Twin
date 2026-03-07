import urllib.request
import json
import os

webhook_url = os.environ.get("FEISHU_WEBHOOK")
if not webhook_url:
    print("Error: Please set FEISHU_WEBHOOK environment variable.")
    exit(1)

with open("/home/liwu/digital_twin/Inbox/detailed_report_for_feishu.md", "r") as f:
    text = f.read()

payload = {
    "msg_type": "text",
    "content": {
        "text": text
    }
}

req = urllib.request.Request(webhook_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=5) as response:
        res = json.loads(response.read().decode())
        if res.get("code") == 0:
            print("Successfully pushed to Feishu.")
        else:
            print(f"Failed to push: {res}")
except Exception as e:
    print(f"Error: {e}")
