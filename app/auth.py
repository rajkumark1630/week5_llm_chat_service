
import secrets

from fastapi import Header, HTTPException, status

from app.config import settings


async def verify_api_key(
    x_api_key: str = Header(default=None)
):
    """
    Verify API key from request header.
    """

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing"
        )

    if not secrets.compare_digest(
        x_api_key,
        settings.api_key
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    return True
