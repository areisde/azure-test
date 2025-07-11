from services import crawler
from . import ingest


def crawl_and_process():
    """
    Crawl all sources, process articles using the ingest logic, and return relevant articles.

    Returns:
        dict: JSON array of processed relevant articles.
    """
    articles = crawler.crawl_all_sources()
    result = ingest.process_articles(articles)
    return {
        "processed": result
    }
