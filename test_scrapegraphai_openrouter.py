from scrapegraphai.graphs import SmartScraperGraph

config = {
    "llm": {
        "provider": "openrouter",
        "api_key": "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",  # <-- Replace with your actual OpenRouter API key
        "base_url": "https://openrouter.ai/api/v1",
        "model": "anthropic/claude-3.5-sonnet",  # You can change to any supported model
        "temperature": 0,
    }
}

graph = SmartScraperGraph(
    prompt="What is the main topic of the page?",
    source="https://scrapegraph-ai.readthedocs.io/en/latest/",
    config=config,
)
result = graph.run()
print(result) 