from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.db.database import get_session
from src.app.models.models import User
from src.app.auth.dependecies import get_current_user, RoleChecker
from .schemas import CreateReviewModel
from .service import ReviewService


router = APIRouter()

review_service = ReviewService()
admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@router.get("/", dependencies=[user_role_checker])
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    reviews = await review_service.get_all_reviews(session)
    return reviews


@router.post("/book/{book_uid}", status_code=status.HTTP_201_CREATED)
async def add_review_to_book(
    book_uid: str,
    review_data: CreateReviewModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review(
        user_email=current_user.email,
        book_uid=book_uid,
        review_data=review_data,
        session=session,
    )

    return new_review


@router.delete(
    "/{review_uid}",
    dependencies=[user_role_checker],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    review_uid: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await review_service.delete_review_from_book(
        review_uid=review_uid, user_email=current_user.email, session=session
    )

    return 
