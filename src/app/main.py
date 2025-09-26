from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.app.db.database import init_db
from src.app.books.routes import router as book_router
from src.app.auth.routes import router as auth_router
from src.app.reviews.routes import router as review_router
from src.app.utils.middleware import register_middleware
from src.app.utils.errors import register_all_errors


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server is starting ...")
    await init_db()
    yield
    print("Server has been stopped")


version = "v1"

app = FastAPI(
    title="Bookly",
    description="A REST API for book review web service",
    version=version,
    lifespan=life_span,
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc"
)

register_all_errors(app)
register_middleware(app)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])
