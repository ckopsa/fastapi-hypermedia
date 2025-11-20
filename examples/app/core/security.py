from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    user_id: str
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = False


async def get_current_user() -> AuthenticatedUser:
    """Return a mock authenticated user for demonstration purposes."""
    return AuthenticatedUser(
        user_id="mock-user-id",
        username="demo",
        email="demo@example.com",
        full_name="Demo User",
        disabled=False
    )


async def get_current_active_user(
        current_user: Annotated[AuthenticatedUser, Depends(get_current_user)]) -> AuthenticatedUser:
    """Check if the current user is active."""
    if current_user.disabled:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
