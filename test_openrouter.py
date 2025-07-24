import os
from dotenv import load_dotenv
load_dotenv()

import openai

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("OPENAI_API_BASE:", os.getenv("OPENAI_API_BASE"))

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

try:
    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, who are you?"}]
    )
    print(response)
except Exception as e:
    print("OpenAI API error:", e) 