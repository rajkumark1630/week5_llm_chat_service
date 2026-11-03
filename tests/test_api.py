
from unittest.mock import patch

import pytest


def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_without_api_key(client, chat_payload):
    response = client.post(
        "/chat/stream",
        json=chat_payload
    )

    assert response.status_code == 401


def test_chat_with_invalid_api_key(
    client,
    chat_payload,
    invalid_auth_headers
):
    response = client.post(
        "/chat/stream",
        json=chat_payload,
        headers=invalid_auth_headers
    )

    assert response.status_code == 403


@patch("app.main.stream_openai")
def test_chat_stream_success(
    mock_stream,
    client,
    chat_payload,
    auth_headers
):
    mock_stream.return_value = iter([
        "Hello ",
        "from ",
        "OpenRouter!"
    ])

    response = client.post(
        "/chat/stream",
        json=chat_payload,
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "text/event-stream"
    )

    assert "Hello " in response.text
    assert "OpenRouter!" in response.text
    assert "[DONE]" in response.text

    mock_stream.assert_called_once()


def test_chat_empty_message(client, auth_headers):
    response = client.post(
        "/chat/stream",
        json={"message": ""},
        headers=auth_headers
    )

    assert response.status_code == 422


def test_usage_endpoint(client, auth_headers):
    response = client.get(
        "/usage",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_requests" in data
    assert "total_tokens" in data
    assert "total_cost_usd" in data


def test_reliability_endpoint(client, auth_headers):
    response = client.get(
        "/reliability",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_requests" in data
    assert "successful_requests" in data
    assert "failed_requests" in data
    assert "success_rate" in data


def test_settings_endpoint(client, auth_headers):
    response = client.get(
        "/settings",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["provider"] == "OpenRouter"
    assert "model" in data
    assert "max_input_tokens" in data


@patch("app.main.get_conversation")
def test_conversation_not_found(
    mock_conversation,
    client,
    auth_headers
):
    mock_conversation.return_value = None

    response = client.get(
        "/conversation/nonexistent",
        headers=auth_headers
    )

    assert response.status_code == 404


@patch("app.main.delete_conversation")
def test_delete_conversation_not_found(
    mock_delete,
    client,
    auth_headers
):
    mock_delete.return_value = False

    response = client.delete(
        "/conversation/nonexistent",
        headers=auth_headers
    )

    assert response.status_code == 404
