from scrapegraphai.graphs import SmartScraperGraph

# Replace with your actual OpenRouter API key
OPENROUTER_API_KEY = "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"

llm_config = {
    "api_key": OPENROUTER_API_KEY,
    "base_url": "https://openrouter.ai/api/v1",
    "model": "openai/gpt-4o",  # Use OpenAI GPT-4o via OpenRouter
    "temperature": 0,
}

# Ask user for prompt and sources
user_prompt = input("Enter your prompt: ")
user_sources = input("Enter one or more URLs, separated by commas: ")
sources = [src.strip() for src in user_sources.split(",") if src.strip()]

results = []
for src in sources:
    print(f"\nScraping: {src}")
    graph = SmartScraperGraph(
        prompt=user_prompt,
        source=src,
        config={"llm": llm_config},
    )
    result = graph.run()
    print(f"Result: {result}")
    results.append({"source": src, "result": result})

print("\nAll results:")
for res in results:
    print(f"Source: {res['source']}\nResult: {res['result']}\n") 