
from fastapi import Depends

from app.auth import verify_api_key
from app.config import settings


async def get_api_key():
    """
    Get and verify API key.
    """
    return await verify_api_key()


def get_settings():
    """
    Return application settings.
    """
    return settings


def get_openrouter_model():
    """
    Return configured OpenRouter model.
    """
    return settings.openrouter_model


def get_max_input_tokens():
    """
    Return maximum allowed input tokens.
    """
    return settings.max_input_tokens


async def get_authenticated_user(
    authenticated: bool = Depends(verify_api_key)
):
    """
    Verify API authentication.
    """
    return authenticated
