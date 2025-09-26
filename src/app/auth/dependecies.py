from fastapi import Request, HTTPException, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from typing import Optional, List, Any
from src.app.utils.security import decode_token
from src.app.db.redis import is_token_in_blocklist
from src.app.db.database import get_session
from src.app.models.models import User
from src.app.utils.errors import AccountNotVerified, InsufficientPermission
from .service import UserService


class TokenBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        creds = await super().__call__(request)

        token = creds.credentials
        token_data = decode_token(token)

        if not self.is_token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please get a new token",
                },
            )

        if await is_token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or has benn revoked",
                    "resolution": "Please get a new token",
                },
            )

        self.verify_token_data(token_data)

        return token_data

    def is_token_valid(self, token: str) -> bool:
        return True if decode_token(token) else False

    def verify_token_data(self, token_data: dict):
        raise NotImplementedError("Please override this method in child classes")


class AccessTokenBearer(TokenBearer):

    def verify_token_data(self, token_data: dict) -> None:

        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an aceess token",
            )


class RefreshTokenBearer(TokenBearer):

    def verify_token_data(self, token_data: dict) -> None:

        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token",
            )


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]
    user_service = UserService()
    user = await user_service.get_user_by_email(user_email, session)
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()

        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()
