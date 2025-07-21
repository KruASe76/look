import asyncio

import logfire
from elasticsearch.dsl import async_connections

from app.core.config import ELASTIC_HOST, ELASTIC_PASSWORD, ELASTIC_USERNAME
from app.service.search.indices import Product

async_connections.create_connection(
    hosts=ELASTIC_HOST, basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
)


async def initialize_elastic() -> None:
    logfire.info("Connecting to Elastic...")

    while True:
        try:
            await Product.init()

            logfire.info("Successfully connected to Elastic.")
            break

        except Exception as e:
            logfire.info("Elastic is not ready yet. Retrying in 3 seconds...", _exc_info=e)
            await asyncio.sleep(3)


async def dispose_elastic() -> None:
    await async_connections.get_connection().close()
