from datetime import datetime
from uuid import UUID

import logfire
from elasticsearch.dsl import AsyncSearch
from elasticsearch.dsl.function import RandomScore
from elasticsearch.dsl.query import (
    Bool,
    FunctionScore,
    Match,
    MatchAll,
    MultiMatch,
    Range,
    Terms,
)
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model import Product, SearchMeta

from .config import PRODUCT_INDEX_NAME
from .indices import Product as ProductDocument
from .util import is_article


class SearchService:
    META_CACHE: SearchMeta | None = None

    @staticmethod
    @logfire.instrument(record_return=True)
    async def search_products(
        user_id: int,  # noqa: ARG004
        query: str | None,
        categories: list[str] | None,
        colors: list[str] | None,
        brands: list[str] | None,
        sizes: list[str] | None,
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

        if sizes:
            filters.append(Terms("sizes", sizes))

        if min_price is not None or max_price is not None:
            price_range = {}

            if min_price is not None:
                price_range["gte"] = min_price
            if max_price is not None:
                price_range["lte"] = max_price

            filters.append(Range("price", price_range))

        if filters:
            search = search.filter(Bool(filter=filters))

        search = search[offset : offset + limit]

        response = await search.execute()

        return [UUID(hit.meta.id) for hit in response.hits]

    @staticmethod
    @logfire.instrument(record_return=True)
    async def get_suggestions(query: str, limit: int) -> list[str]:
        search = AsyncSearch(index=PRODUCT_INDEX_NAME).source(fields=["name_suggest"])

        if query:
            search = search.query(
                MultiMatch(
                    query=query,
                    fields=[
                        "name_suggest",
                        "name_suggest._2gram",
                        "name_suggest._3gram",
                    ],
                    type="bool_prefix",
                )
            )
        else:
            search = search.query(
                FunctionScore(query=MatchAll(), functions=[RandomScore()])
            )

        search = search[0:limit]

        response = await search.execute()

        return [hit.name_suggest for hit in response.hits]

    # noinspection Pydantic
    @classmethod
    @logfire.instrument(record_return=True)
    async def get_meta(cls, session: AsyncSession) -> SearchMeta:
        if not cls.META_CACHE:
            field_to_column = {
                "categories": Product.category,
                "colors": Product.color_name,
                "brands": Product.brand,
            }

            cls.META_CACHE = SearchMeta(
                **{
                    field: sorted((await session.exec(select(column).distinct())).all())
                    for field, column in field_to_column.items()
                }
            )

        return cls.META_CACHE

    @classmethod
    @logfire.instrument(record_return=True)
    async def refresh_meta_cache(cls, session: AsyncSession) -> SearchMeta:
        cls.META_CACHE = None
        return await cls.get_meta(session)

    # noinspection PyTypeChecker,Pydantic
    @staticmethod
    @logfire.instrument(record_return=True)
    async def sync_products(session: AsyncSession, since: datetime) -> int:
        """
        :return: number of products synced
        """

        statement = select(Product).where(Product.updated_at >= since)
        products = (await session.exec(statement)).all()

        for product in products:
            await ProductDocument.from_product(product).save()

        return len(products)
