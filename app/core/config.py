import os

from sqlalchemy import URL

# BUSINESS

APP_TITLE = "Look"

INIT_DATA_SCHEME_NAME = "tma"
INIT_DATA_DESCRIPTION = "Telegram MiniApp init-data"


class Defaults:
    collection_name = "__FAVOURITES__"
    collection_cover_image_url = (
        "https://static.vecteezy.com/system/resources/previews/023/465/809/original/"
        "add-bookmark-dark-mode-glyph-ui-icon-saving-webpage-reading-list-user-interface-"
        "design-white-silhouette-symbol-on-black-space-solid-pictogram-for-web-mobile-"
        "isolated-illustration-vector.jpg"
    )


class SpecialUserIds:
    GLOBAL_TRENDS = 1
    GLOBAL_BRANDS = 2
    PERSONAL_TRENDS = 3
    PERSONAL_BRANDS = 4


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
