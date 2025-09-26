from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from src.app.books.schemas import Book
from src.app.reviews.schemas import ReviewModel


class CreateUserModel(BaseModel):
    first_name: str = Field(max_length=40)
    last_name: str = Field(max_length=40)
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6, max_length=36)


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6, max_length=36)


class UserResponse(BaseModel):
    uid: str
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: datetime


class UserBooksModel(UserResponse):
    books: List[Book]
    reviews: List[ReviewModel]


class EmailModel(BaseModel):
    addresses : List[str]


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str