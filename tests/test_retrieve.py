import azure.functions as func
import json
import os
import datetime
from unittest.mock import patch
from function_app import retrieve_articles


def test_retrieve_articles():
    req = func.HttpRequest(
        method="GET",
        url="/api/retrieve",
        body=None,
        headers={}
    )

    response = retrieve_articles(req)
    assert response.status_code == 200
    
    results = json.loads(response.get_body())
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
        
        