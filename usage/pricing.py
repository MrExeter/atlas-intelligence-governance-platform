PRICING = {
    "llm": {
        "openai:gpt-4o-mini": {
            "input_per_1k": 0.00015,
            "output_per_1k": 0.00060,
        },
        "openai:gpt-4o": {
            "input_per_1k": 0.00250,
            "output_per_1k": 0.01000,
        },
        "openai:gpt-4.1": {
            "input_per_1k": 0.00200,
            "output_per_1k": 0.00800,
        },
    },
    "api": {
        "tavily": {
            "per_call": 0.004,
        },
        "newsdata": {
            "per_call": 0.001,
        },
        "google_news_rss": {
            "per_call": 0.0,
        },
        "hackernews": {
            "per_call": 0.0,
        },
    },
}
