__all__ = ["app"]

from fastapi import FastAPI

from app.core.config import APP_TITLE

from .lifespan import lifespan
from .route import setup_routing

app = FastAPI(title=APP_TITLE, lifespan=lifespan)

setup_routing(app)
