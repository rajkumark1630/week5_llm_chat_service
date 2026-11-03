
from unittest.mock import patch, MagicMock

import pytest

from app.llm import (
    count_tokens,
    calculate_cost,
    ask_openai,
    log_usage
)


def test_count_tokens():
    messages = [
        {"role": "user", "content": "Hello AI"}
    ]

    result = count_tokens(messages)

    assert isinstance(result, int)
    assert result > 0


def test_calculate_cost():
    cost = calculate_cost(
        input_tokens=1000,
        output_tokens=500
    )

    assert isinstance(cost, float)
    assert cost > 0


def test_calculate_cost_zero_tokens():
    cost = calculate_cost(0, 0)

    assert cost == 0


@patch("app.llm.openai_client.chat.completions.create")
def test_ask_openai_success(mock_create):

    mock_response = MagicMock()

    mock_response.choices[0].message.content = "Hello from AI"

    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20

    mock_create.return_value = mock_response

    with patch("app.llm.log_usage") as mock_log:

        with patch("app.llm.log_request") as mock_reliability:

            result = ask_openai("Hello")

            assert result == "Hello from AI"

            mock_create.assert_called_once()
            mock_log.assert_called_once()
            mock_reliability.assert_called_once_with(
                "success",
                pytest.approx(mock_reliability.call_args[0][1])
            )


@patch("app.llm.openai_client.chat.completions.create")
def test_ask_openai_api_error(mock_create):

    mock_create.side_effect = Exception("API connection failed")

    with patch("app.llm.log_request") as mock_log:

        with pytest.raises(Exception):
            ask_openai("Hello")

        mock_log.assert_called_once()

        assert mock_log.call_args[0][0] == "failed"


def test_log_usage(tmp_path, monkeypatch):

    test_file = tmp_path / "usage.jsonl"

    monkeypatch.chdir(tmp_path)

    log_usage(
        model="openai/gpt-4o-mini",
        input_tokens=100,
        output_tokens=50,
        cost=0.001
    )

    assert test_file.exists()

    import json

    with open(test_file, "r", encoding="utf-8") as file:
        record = json.loads(file.readline())

    assert record["model"] == "openai/gpt-4o-mini"
    assert record["input_tokens"] == 100
    assert record["output_tokens"] == 50
    assert record["total_tokens"] == 150
    assert record["cost_usd"] == 0.001
