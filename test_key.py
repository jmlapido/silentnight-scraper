import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

# Get API key from environment or use the hardcoded one
api_key = os.getenv("OPENROUTER_API_KEY", "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")
print(f"Using API key: {api_key[:10]}...{api_key[-5:]}")

# OpenRouter API endpoint
url = "https://openrouter.ai/api/v1/chat/completions"

# Headers with authorization
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Simple prompt
data = {
    "model": "openai/gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Say hello world"}
    ]
}

print("Sending request to OpenRouter API...")
try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # If successful, show the response content
    if response.status_code == 200:
        content = response.json()
        if 'choices' in content and len(content['choices']) > 0:
            message = content['choices'][0]['message']['content']
            print(f"AI response: {message}")
        else:
            print("No response content found.")
except Exception as e:
    print(f"Error: {e}") 