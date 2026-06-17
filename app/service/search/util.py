import re
import time

article_regex = re.compile(r"^[a-z\-]*\d[a-z\-]*$", re.IGNORECASE)


def is_article(query: str) -> bool:
    return article_regex.fullmatch(query) is not None


def get_current_hour_seed() -> int:
    return int(time.time() / 3600)
