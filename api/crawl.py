import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path)

from services.crawler import crawl_all_sources
from api.ingest import process_articles


def crawl_and_process():
    """
    Crawl all sources, process articles using the ingest logic, and return relevant articles.

    Returns:
        dict: JSON array of processed relevant articles.
    """
    articles = crawl_all_sources()
    result = process_articles(articles)
    return {
        "processed": result
    }
