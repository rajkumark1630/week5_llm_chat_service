
import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.config import settings


@pytest.fixture
def client():
    """
    Create FastAPI test client.
    """

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_api_key():
    """
    Return valid API key for testing.
    """

    return settings.api_key


@pytest.fixture
def auth_headers(valid_api_key):
    """
    Return authentication headers.
    """

    return {
        "X-API-Key": valid_api_key
    }


@pytest.fixture
def invalid_auth_headers():
    """
    Return invalid authentication headers.
    """

    return {
        "X-API-Key": "invalid-test-api-key"
    }


@pytest.fixture
def chat_payload():
    """
    Return sample chat request.
    """

    return {
        "message": "Explain Python in simple words"
    }


@pytest.fixture
def conversation_payload():
    """
    Return conversation request.
    """

    return {
        "message": "Hello AI",
        "conversation_id": "test-conversation-001"
    }
