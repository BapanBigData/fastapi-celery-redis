from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.mysql as ms
from datetime import datetime
from sqlalchemy import String
import uuid
from typing import List, Optional
from datetime import date


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: str = Field(
        sa_column=Column(
            String(36),
            nullable=False,
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
        )
    )

    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    role: str = Field(
        sa_column=Column(ms.VARCHAR(255), nullable=False, server_default="user")
    )
    created_at: datetime = Field(sa_column=Column(ms.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(ms.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self) -> str:
        return f"User: {self.username}"


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: str = Field(
        sa_column=Column(
            String(36),
            nullable=False,
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
        )
    )

    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[str] = Field(default=None, foreign_key="users.uid")
    created_at: datetime = Field(sa_column=Column(ms.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(ms.TIMESTAMP, default=datetime.now))
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self) -> str:
        return f"<Book: {self.title}>"


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: str = Field(
        sa_column=Column(
            String(36),
            nullable=False,
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
        )
    )
    rating: float = Field(gt=0, le=5)
    review_text: str
    user_uid: Optional[str] = Field(default=None, foreign_key="users.uid")
    book_uid: Optional[str] = Field(default=None, foreign_key="books.uid")
    created_at: datetime = Field(sa_column=Column(ms.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(ms.TIMESTAMP, default=datetime.now))
    user: Optional["User"] = Relationship(back_populates="reviews")
    book: Optional["Book"] = Relationship(back_populates="reviews")

    def __repr__(self) -> str:
        return f"Review for {self.book_uid} by the user {self.user_uid}>"
