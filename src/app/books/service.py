from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from src.app.models.models import Book
from sqlmodel import select, desc


class BookService:

    async def get_all_book(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))

        result = await session.exec(statement)

        return result.all()

    async def get_user_book(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )

        result = await session.exec(statement)

        books = result.all()

        return books if books else None

    async def get_book(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)

        result = await session.exec(statement)

        book = result.first()

        return book if book else None

    async def create_book(
        self, book_data: BookCreateModel, user_uid: str, session: AsyncSession
    ):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)

        new_book.user_uid = user_uid

        session.add(new_book)
        await session.commit()

        return new_book

    async def update_book(
        self, book_uid: str, book_update_data: BookUpdateModel, session: AsyncSession
    ):
        book_to_update = await self.get_book(book_uid, session)

        if book_to_update:

            update_book_data_dict = book_update_data.model_dump()

            for k, v in update_book_data_dict.items():
                setattr(book_to_update, k, v)

            await session.commit()

            return book_to_update

        return None

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book(book_uid, session)

        if book_to_delete:

            await session.delete(book_to_delete)

            await session.commit()

            return {"status": "ok"}

        return None
