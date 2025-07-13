from elasticsearch.dsl import async_connections

from app.core.config import ELASTIC_HOST, ELASTIC_PASSWORD, ELASTIC_USERNAME
from app.service.search.indices import Product

async_connections.create_connection(hosts=ELASTIC_HOST, basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD))


async def initialize_elastic() -> None:
    await Product.init()


async def dispose_elastic() -> None:
    await async_connections.get_connection().close()
