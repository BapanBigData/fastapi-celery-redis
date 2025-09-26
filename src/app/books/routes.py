from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from src.app.books.service import BookService
from src.app.books.schemas import (
    BookCreateModel,
    BookUpdateModel,
    Book,
    BookDetailsModel,
)
from src.app.db.database import get_session
from src.app.auth.dependecies import AccessTokenBearer, RoleChecker


router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


@router.get(
    "/",
    response_model=List[Book],
    status_code=status.HTTP_200_OK,
    dependencies=[role_checker],
)
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):

    books = await book_service.get_all_book(session)
    return books


@router.post(
    "/{create_book}",
    response_model=Book,
    status_code=status.HTTP_201_CREATED,
    dependencies=[role_checker],
)
async def create_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    user_uid = token_details["user"]["user_uid"]
    new_book = await book_service.create_book(book_data, user_uid, session)

    return new_book


@router.get(
    "/me",
    response_model=List[Book],
    status_code=status.HTTP_200_OK,
    dependencies=[role_checker],
)
async def get_book(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    user_uid = token_details["user"]["user_uid"]
    books = await book_service.get_user_book(user_uid, session)

    if books:
        return books

    return []


@router.get("/{book_uid}", response_model=BookDetailsModel, dependencies=[role_checker])
async def get_book_by_uid(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(access_token_bearer),
) -> dict:
    book = await book_service.get_book(book_uid, session)

    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )


@router.patch(
    "/{book_uid}",
    response_model=Book,
    status_code=status.HTTP_200_OK,
    dependencies=[role_checker],
)
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):

    updated_book = await book_service.update_book(book_uid, book_update_data, session)

    if updated_book:
        return updated_book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@router.delete(
    "/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):

    delete_success = await book_service.delete_book(book_uid, session)

    if delete_success:
        return None

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
