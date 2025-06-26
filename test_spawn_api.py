"""Test spawning a minion via the API"""

import requests
import json

# Test the spawn endpoint
url = "http://localhost:8000/api/v2/minions/spawn"
payload = {
    "name": "TestBot",
    "personality": "Witty",
    "quirks": ["makes puns", "loves dad jokes"],
    "catchphrases": ["That's pun-believable!", "Let me compute that..."]
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
