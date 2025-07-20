__all__ = ["app"]

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import ALLOW_ORIGINS, APP_TITLE

from .route import register_exception_handlers, root_router
from .util import lifespan

app = FastAPI(title=APP_TITLE, lifespan=lifespan)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router)
register_exception_handlers(app)
