from datetime import datetime
from uuid import UUID

import logfire
from elasticsearch.dsl import AsyncSearch
from elasticsearch.dsl.query import Match, MultiMatch, Range, Terms
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model import Product

from .config import PRODUCT_INDEX_NAME
from .indices import Product as ProductDocument
from .util import is_article


class SearchService:
    # noinspection PyTypeChecker,Pydantic
    @staticmethod
    @logfire.instrument()
    async def sync_products(session: AsyncSession, since: datetime) -> int:
        """
        :return: number of products synced
        """

        statement = select(Product).where(Product.updated_at > since)
        products = (await session.exec(statement)).all()

        for product in products:
            await ProductDocument.from_product(product).save()

        return len(products)

    @staticmethod
    @logfire.instrument(record_return=True)
    async def search_products(
        user_id: int,  # noqa: ARG004
        query: str | None,
        categories: list[str] | None,
        colors: list[str] | None,
        brands: list[str] | None,
        min_price: float | None,
        max_price: float | None,
        limit: int,
        offset: int,
    ) -> list[UUID]:
        search = AsyncSearch(index=PRODUCT_INDEX_NAME).source(fields=False)

        if query:
            if is_article(query):
                # noinspection PyTypeChecker
                search = search.query(Match("article", query))
            else:
                search = search.query(
                    MultiMatch(
                        query=query,
                        fields=[
                            "name^3",
                            "category^3",
                            "color_name^2",
                            "brand^2",
                            "description^1",
                        ],
                        fuzziness="AUTO",
                    )
                )

        filters = []

        if categories:
            filters.append(Terms("category", categories))

        if colors:
            filters.append(Terms("color_name", colors))

        if brands:
            filters.append(Terms("brand", brands))

        if min_price is not None or max_price is not None:
            price_range = {}

            if min_price is not None:
                price_range["gte"] = min_price
            if max_price is not None:
                price_range["lte"] = max_price

            filters.append(Range("price", **price_range))

        if filters:
            search = search.filter(*filters)

        search = search[offset : offset + limit]

        response = await search.execute()

        return [UUID(hit.meta.id) for hit in response.hits]
