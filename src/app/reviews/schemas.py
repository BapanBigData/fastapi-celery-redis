from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReviewModel(BaseModel):
    uid: str
    rating: float = Field(gt=0, le=5)
    review_text: str
    user_uid: Optional[str]
    book_uid: Optional[str]
    created_at: datetime
    updated_at: datetime


class CreateReviewModel(BaseModel):
    rating: float = Field(gt=0, le=5)
    review_text: str
