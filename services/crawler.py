import feedparser
from datetime import datetime
from typing import List, Dict
from db.crud import get_sources
import html
from bs4 import BeautifulSoup

def load_sources() -> tuple[List[str], List[str]]:
    """
    Loads sources from the database using get_sources().
    Returns:
        rss_feeds (list): List of RSS feed URLs.
        subreddits (list): List of subreddit names.
    """
    sources = get_sources()
    rss_feeds = [s['url'] for s in sources if s['type'] == 'rss']
    subreddits = [s['name'] for s in sources if s['type'] == 'reddit']
    return rss_feeds, subreddits


def fetch_rss_articles(rss_urls: List[str]) -> List[Dict]:
    """Fetches articles from a list of RSS feed URLs.
    Args:
        rss_urls (List[str]): List of RSS feed URLs.
    Returns:
        List[Dict]: List of articles with keys: id, title, body, published_at
    """
    articles = []
    for url in rss_urls:
        source = url.split('.')[1]  # Extract source from URL
        feed = feedparser.parse(url) # Fetch and parse the RSS feed
        if 'entries' not in feed:
            return articles  # Return empty if no entries found
        for entry in feed.entries:
            summary_raw = entry.get('summary', '')
            summary_clean = BeautifulSoup(html.unescape(summary_raw), "html.parser").get_text(separator="\n", strip=True)
            article = {
                'id': entry.get('id', entry.get('link', '')),
                'title': entry.get('title', ''),
                'body': summary_clean,
                'published_at': entry.get('published', ''),
                'source': source
            }
            articles.append(article)
    return articles


def fetch_reddit_articles(subreddits: List[str]) -> List[Dict]:
    pass  # Placeholder for Reddit fetching logic


def crawl_all_sources() -> List[Dict]:
    """
    Main crawler function that fetches articles from all sources specified in the database.
    Returns:
        List[Dict]: Combined list of articles from RSS feeds and Reddit.
    """
    rss_feeds, subreddits = load_sources()
    articles = []
    
    if rss_feeds:
        articles.extend(fetch_rss_articles(rss_feeds))
    if subreddits:
        articles.extend(fetch_reddit_articles(subreddits))
    return articles

if __name__ == '__main__':
    articles = crawl_all_sources()
