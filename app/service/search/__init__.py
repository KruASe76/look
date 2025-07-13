from typing import Any

import logfire
from elasticsearch.dsl import AsyncSearch
from elasticsearch.dsl.query import Match, MultiMatch, Range, Terms

from app.model import AuthenticatedUser

from .config import PRODUCT_INDEX_NAME
from .util import is_article


class SearchService:
    @staticmethod
    @logfire.instrument(record_return=True)
    async def search_products(
        user: AuthenticatedUser,  # noqa: ARG004
        query: str | None,
        categories: list[str] | None,
        colors: list[str] | None,
        brands: list[str] | None,
        min_price: float | None,
        max_price: float | None,
        limit: int,
        offset: int,
    ) -> list[Any]:
        search = AsyncSearch(index=PRODUCT_INDEX_NAME)

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

        return response.hits
