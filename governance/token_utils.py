from governance.cost_estimator import estimate_cost


def update_token_usage(state, response):
    """
    Extract token usage from an LLM response and update state totals.
    """

    usage = response.response_metadata.get("token_usage", {})

    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)

    cost_usd = estimate_cost(prompt_tokens, completion_tokens)

    return {
        "tokens_used": int(state.get("tokens_used", 0) + total_tokens),
        "cost_usd": float(state.get("cost_usd", 0) + cost_usd)
    }
