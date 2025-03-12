__all__ = ["app"]

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from .route import root_router
from .util import lifespan

app = FastAPI(title="Look", lifespan=lifespan)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)

app.include_router(root_router)


@app.get("/", include_in_schema=False, response_model=None)
async def docs_redirect() -> ...:
    return RedirectResponse(url="/docs")
