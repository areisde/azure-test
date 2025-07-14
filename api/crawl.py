from services import crawler
from . import ingest
import logging


def crawl_and_process():
    """
    Crawl all sources, process articles using the ingest logic, and return relevant articles.

    Returns:
        dict: JSON array of processed relevant articles.
    """
    articles = crawler.crawl_all_sources()
    logging.info("Done crawling latest news.")

    relevant_articles = ingest.ingest_articles(articles)

    return relevant_articles
