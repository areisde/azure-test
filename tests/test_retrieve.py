import json
import os
import datetime
from unittest.mock import patch
from api import retrieve

def load_test_articles():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FILE_PATH = os.path.join(BASE_DIR, "data", "test.json")
    with open(FILE_PATH, "r") as f:
        return json.load(f)

def test_retrieve_articles():
    results = retrieve.retrieve_events()

    assert isinstance(results, list)

    for item in results:
        assert isinstance(item, dict)
        assert "id" in item and isinstance(item["id"], str)
        assert "source" in item and isinstance(item["source"], str)
        assert "title" in item and isinstance(item["title"], str)
        if "body" in item:
            assert item["body"] is None or isinstance(item["body"], str)
        assert "published_at" in item
        try:
            datetime.datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))
        except ValueError:
            assert False, f"Invalid timestamp: {item['published_at']}"
        
        