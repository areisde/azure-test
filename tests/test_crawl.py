import azure.functions as func
import json
from function_app import crawl_articles
from unittest.mock import patch

@patch("api.crawl.ingest.ingest_articles")
def test_crawl_route_with_mocked_ingest(mock_ingest):
    mock_ingest.return_value = [
        # Return fake "relevant" article objects
        type("MockArticle", (), {"title": "Fake Article 1"})(),
        type("MockArticle", (), {"title": "Fake Article 2"})()
    ]

    req = func.HttpRequest(
        method="GET",
        url="/api/crawl",
        body=None,
        headers={}
    )

    response = crawl_articles(req)

    assert response.status_code == 200
    result = json.loads(response.get_body())
    assert "Relevant articles" in result
    assert result["Relevant articles"] == ["Fake Article 1", "Fake Article 2"]