from pydantic import BaseModel
from datetime import datetime, date
from typing import List
from src.app.reviews.schemas import ReviewModel


class Book(BaseModel):
    uid: str
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime


class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


class BookDetailsModel(Book):
    reviews: List[ReviewModel]
