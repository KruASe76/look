__all__ = ["POSTGRES_URL"]


import os

postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT")
postgres_db = os.getenv("POSTGRES_DB")
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")

POSTGRES_URL = (
    f"postgresql+asyncpg://"
    f"{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
)
