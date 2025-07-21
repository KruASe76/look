import os

from sqlalchemy import URL

# TECHNICAL

DEV_API_KEY = os.getenv("DEV_API_KEY")

BOT_TOKEN = os.getenv("BOT_TOKEN")

POSTGRES_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DB"),
)

ELASTIC_HOST = os.getenv("ELASTIC_HOST")
ELASTIC_USERNAME = os.getenv("ELASTIC_USERNAME")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")

LOGFIRE_SERVICE_NAME = os.getenv("LOGFIRE_SERVICE_NAME")
LOGFIRE_ENVIRONMENT = os.getenv("LOGFIRE_ENVIRONMENT")

ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", default="*").split(",")


# BUSINESS

APP_TITLE = "Look"

INIT_DATA_SCHEME_NAME = "tma"
INIT_DATA_DESCRIPTION = "Telegram MiniApp init-data"

DEFAULT_COLLECTION_NAME = "__FAVOURITES__"

TRENDS_USER_ID = 1
BRANDS_USER_ID = 2
