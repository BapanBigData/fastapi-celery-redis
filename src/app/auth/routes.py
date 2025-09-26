from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta, datetime
from .schemas import (
    CreateUserModel,
    UserLoginModel,
    UserBooksModel,
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
)
from .service import UserService
from src.app.db.database import get_session
from src.app.utils.security import (
    create_access_token,
    verify_password,
    create_url_safe_token,
    decode_url_safe_token,
)
from .dependecies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from src.app.db.redis import add_jti_to_blocklist
from src.app.utils.config import Config
from src.app.utils.errors import UserNotFound, UserAlreadyExists
from src.app.utils.security import generate_password_hash
from src.app.utils.celery_tasks import send_email


router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2


@router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses

    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to our app"

    send_email.delay(emails, subject, html)

    return {"message": "Email sent successfully"}


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_Account(
    user_data: CreateUserModel,
    session: AsyncSession = Depends(get_session),
):
    """
    Create user account using email, username, first_name, last_name
    params:
        user_data: UserCreateModel
    """
    email = user_data.email

    user_exists = await user_service.is_user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """

    emails = [email]

    subject = "Verify Your email"

    send_email.delay(emails, subject, html)

    return {
        "message": "Account Created! Check email to verify your account",
        "user": new_user,
    }


@router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@router.post("/login")
async def login_users(
    user_login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = user_login_data.email
    password = user_login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={"email": email, "user_uid": str(user.uid), "role": user.role}
            )

            refresh_token = create_access_token(
                user_data={
                    "email": email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "User login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                }
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please check your password and try again.",
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found. Please verify the email address and try again.",
    )


@router.get("/new_session")
async def get_new_session(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
    )


@router.get("/me", response_model=UserBooksModel)
async def current_user(user=Depends(get_current_user), _: bool = Depends(role_checker)):
    return user


@router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):

    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out succesfully"}, status_code=status.HTTP_200_OK
    )


@router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    subject = "Reset Your Password"

    send_email.delay([email], subject, html_message)
    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password

    if new_password != confirm_password:
        raise HTTPException(
            detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        password_hash = generate_password_hash(new_password)
        await user_service.update_user(user, {"password_hash": password_hash}, session)

        return JSONResponse(
            content={"message": "Password reset Successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
