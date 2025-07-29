__all__ = ["app"]

from fastapi import FastAPI

from app.core.config import APP_TITLE

from .route import setup_routing
from .util import lifespan

app = FastAPI(title=APP_TITLE, lifespan=lifespan)

setup_routing(app)
