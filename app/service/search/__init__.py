from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

import logfire
import pg_async_events
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

from app.database import start_readonly_session
from app.model import Product, SearchMeta
from app.util import AsyncRWLock

from .config import PRODUCT_INDEX_NAME
from .indices import Product as ProductDocument
from .util import is_article

META_REFRESH_NOTIFICATION_CHANNEL = "search_meta_refresh"


class SearchService:
    _meta_cache: SearchMeta
    _meta_cache_lock = AsyncRWLock()

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
                article_search = search.query(Match("article", query))
                article_response = await article_search.execute()

                if len(article_response.hits) == 1:
                    return [UUID(hit.meta.id) for hit in article_response.hits]

            search = search.query(
                MultiMatch(
                    query=query,
                    fields=["name^3", "category^3", "color_name^2", "brand^2", "description^1"],
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

        if not query and not filters:
            search = search.query(FunctionScore(query=MatchAll(), functions=[RandomScore()]))

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
                    fields=["name_suggest", "name_suggest._2gram", "name_suggest._3gram"],
                    type="bool_prefix",
                )
            )
        else:
            search = search.query(FunctionScore(query=MatchAll(), functions=[RandomScore()]))

        search = search[0:limit]

        response = await search.execute()

        return [hit.name_suggest for hit in response.hits]

    # noinspection PyTypeChecker,Pydantic
    @staticmethod
    @logfire.instrument(record_return=True)
    async def sync_products(session: AsyncSession, since: datetime) -> int:
        """
        Sync product index with database.

        :return: number of products synced
        """
        statement = select(Product).where(Product.updated_at >= since)
        products = (await session.exec(statement)).all()

        for product in products:
            await ProductDocument.from_product(product).save()

        return len(products)

    @classmethod
    @logfire.instrument(record_return=True)
    async def get_meta(cls) -> SearchMeta:
        async with cls._meta_cache_lock.read():
            return cls._meta_cache

    @classmethod
    @logfire.instrument
    async def refresh_meta(cls) -> None:
        await pg_async_events.notify(META_REFRESH_NOTIFICATION_CHANNEL, None)

    @classmethod
    async def meta_refresh_listener(cls) -> None:
        async for _notification in pg_async_events.subscribe(META_REFRESH_NOTIFICATION_CHANNEL):
            await cls.handle_meta_refresh_notification()

    @classmethod
    @logfire.instrument
    async def handle_meta_refresh_notification(cls) -> None:
        async with start_readonly_session() as session:
            new_meta = await cls._compute_meta(session=session)

        async with cls._meta_cache_lock.write():
            cls._meta_cache = new_meta

    # noinspection PyTypeChecker,Pydantic
    @classmethod
    @logfire.instrument(record_return=True)
    async def _compute_meta(cls, session: AsyncSession) -> SearchMeta:
        all_brands: Sequence[str] = (
            (
                await session.exec(
                    select(Product.brand).distinct().order_by(Product.brand)
                )
            ).all()
        )  # fmt: skip
        all_categories: Sequence[str] = (
            (
                await session.exec(
                    select(Product.category).distinct().order_by(Product.category)
                )
            ).all()
        )  # fmt: skip
        color_dict: dict[str, str] = dict(
            (
                await session.exec(
                    select(Product.color_name, Product.color_code)
                    .distinct(Product.color_name)  # postgres-specific
                    .order_by(Product.color_name)
                )
            ).all()
        )

        return SearchMeta(brands=all_brands, categories=all_categories, colors=color_dict)
