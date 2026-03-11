from governance.token_utils import update_token_usage


class MockResponse:
    response_metadata = {
        "token_usage": {
            "prompt_tokens": 1000,
            "completion_tokens": 500,
            "total_tokens": 1500
        }
    }


def test_token_usage_update():

    state = {
        "tokens_used": 100,
        "cost_usd": 0.001
    }

    response = MockResponse()

    result = update_token_usage(state, response)

    assert result["tokens_used"] == 1600
    assert result["cost_usd"] > 0
