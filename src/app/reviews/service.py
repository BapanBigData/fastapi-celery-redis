import logging
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import select, desc
from src.app.auth.service import UserService
from src.app.books.service import BookService
from src.app.models.models import Review
from .schemas import CreateReviewModel

book_service = BookService()
user_service = UserService()


class ReviewService:

    async def add_review(
        self,
        user_email: str,
        book_uid: str,
        review_data: CreateReviewModel,
        session: AsyncSession,
    ):
        try:
            book = await book_service.get_book(book_uid=book_uid, session=session)
            user = await user_service.get_user_by_email(
                email=user_email, session=session
            )

            review_data_dict = review_data.model_dump()
            new_review = Review(**review_data_dict)

            if not book:
                raise HTTPException(
                    detail="Book not found", status_code=status.HTTP_404_NOT_FOUND
                )

            if not user:
                raise HTTPException(
                    detail="User not found", status_code=status.HTTP_404_NOT_FOUND
                )

            new_review.user = user
            new_review.book = book

            session.add(new_review)
            await session.commit()

            return new_review

        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oops ... something went wrong!",
            )

    async def get_review(self, review_uid: str, session: AsyncSession):
        statement = select(Review).where(Review.uid == review_uid)

        result = await session.exec(statement)

        return result.first()

    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))

        result = await session.exec(statement)

        return result.all()

    async def delete_review_from_book(
        self, review_uid: str, user_email: str, session: AsyncSession
    ):
        user = await user_service.get_user_by_email(user_email, session)

        review = await self.get_review(review_uid, session)

        if not review or (review.user != user):
            raise HTTPException(
                detail="Cannot delete this review",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        await session.delete(review)

        await session.commit()
