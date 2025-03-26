__all__ = ["app"]

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import ALLOW_ORIGINS

from .route import root_router
from .util import lifespan

app = FastAPI(title="Look", lifespan=lifespan)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router)
