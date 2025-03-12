__all__ = ["app"]

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .route import root_router
from .util import lifespan

app = FastAPI(title="Look", lifespan=lifespan)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(root_router)
