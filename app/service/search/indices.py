from typing import ClassVar, Self

from elasticsearch.dsl import (
    AsyncDocument,
    Float,
    Keyword,
    SearchAsYouType,
    Text,
    analysis,
)

from app.model import Product as ProductModel

from .config import PRODUCT_INDEX_NAME

russian_analyzer = analysis.analyzer(
    "russian_analyzer",
    tokenizer="standard",
    filter=[
        "lowercase",
        analysis.token_filter("russian_stop", type="stop", stopwords="_russian_"),
        analysis.token_filter("russian_stemmer", type="stemmer", language="russian"),
    ],
)


class Product(AsyncDocument):
    article = Keyword()
    name = Text(analyzer=russian_analyzer, fields={"raw": Keyword()})
    name_suggest = SearchAsYouType(analyzer=russian_analyzer)
    brand = Keyword()
    category = Keyword()
    color_name = Keyword()
    description = Text(analyzer=russian_analyzer)
    price = Float()

    class Index:
        name = PRODUCT_INDEX_NAME
        settings: ClassVar = {"number_of_shards": 1, "number_of_replicas": 0}
        analyzers: ClassVar = [russian_analyzer]

    # noinspection PyArgumentList
    @classmethod
    def from_product(cls, product: ProductModel) -> Self:
        return cls(
            meta={"id": product.id},
            article=product.article,
            name=product.name,
            name_suggest=product.name,
            brand=product.brand,
            category=product.category,
            color_name=product.color_name,
            description=product.description,
            price=product.discount_price,
        )
