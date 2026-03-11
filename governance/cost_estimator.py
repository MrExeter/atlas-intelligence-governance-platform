def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """
    Estimate OpenAI request cost based on token usage.
    """

    INPUT_COST_PER_1K = 0.005
    OUTPUT_COST_PER_1K = 0.015

    input_cost = (prompt_tokens / 1000) * INPUT_COST_PER_1K
    output_cost = (completion_tokens / 1000) * OUTPUT_COST_PER_1K

    return round(input_cost + output_cost, 6)
