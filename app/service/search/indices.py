from typing import ClassVar

from elasticsearch.dsl import AsyncDocument, Float, Keyword, Text, analysis

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
    brand = Keyword()
    category = Keyword()
    color_name = Keyword()
    description = Text(analyzer=russian_analyzer)
    price = Float()

    class Index:
        name = PRODUCT_INDEX_NAME
        settings: ClassVar = {"number_of_shards": 1, "number_of_replicas": 0}
        analyzers: ClassVar = [russian_analyzer]
