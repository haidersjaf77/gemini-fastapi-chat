import requests
import json
from datetime import datetime

url = "url/chat"

data = {
    "prompt": "Give me the perfect excuse to cancel plans tonight that's creative but believable.",
    "email": "your-mail",
    "api_key": "your-generatedapikey"
}

response = requests.post(url, json=data)
reply = response.json().get("reply")

# Print to terminal
print("🤖 Bot reply:", reply)

# Save conversation to a JSON file with timestamp
conversation = {
    "timestamp": datetime.now().isoformat(),
    "email": data["email"],
    "prompt": data["prompt"],
    "reply": reply
}

with open("replies.json", "a", encoding="utf-8") as f:
    f.write(json.dumps(conversation, ensure_ascii=False) + "\n")
