import re

article_regex = re.compile(r"^[a-z\-]*\d[a-z\-]*$", re.IGNORECASE)


def is_article(query: str) -> bool:
    return article_regex.fullmatch(query) is not None
