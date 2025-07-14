from urllib3 import response
import azure.functions as func
import json
from function_app import ingest_articles
import pytest
from unittest.mock import patch
import os

def load_test_articles():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FILE_PATH = os.path.join(BASE_DIR, "data", "test.json")
    with open(FILE_PATH, "r") as f:
        return json.load(f)

@patch("api.ingest.crud.upload_articles")
def test_ingest_json_array(mock_upload):
    mock_upload.return_value = True # Mock DB upload
    data = load_test_articles() # Load data

    req = func.HttpRequest(
        method="POST",
        body=json.dumps(data).encode("utf-8"),
        url="/api/ingest",
        headers={"Content-Type": "application/json"}
    )

    # Call the function
    response = ingest_articles(req)

    assert response.status_code == 200
    result = json.loads(response.get_body())

    # Compute precision
    true_positives = sum(1 for art in data if art["relevant"] is True)
    precision = true_positives/result["count"] # Formula for computing precision

    assert result["message"] == "Articles ingested successfully."
    assert precision >= 0.7 # At least 70% of articles were well classified


@patch("api.ingest.crud.upload_articles")
def test_ingest_json_stream(mock_upload):
    mock_upload.return_value = True # Mock DB upload
    data = load_test_articles() # Load data
    ndjson = "\n".join(json.dumps(a) for a in data) # Mock stream format

    req = func.HttpRequest(
        method="POST",
        body=ndjson.encode("utf-8"),
        url="/api/ingest",
        headers={"Content-Type": "application/json"}
    )

    # Call the function
    response = ingest_articles(req)

    assert response.status_code == 200
    result = json.loads(response.get_body())

    # Compute precision
    true_positives = sum(1 for art in data if art["relevant"] is True)
    precision = true_positives/result["count"] # Formula for computing precision

    assert result["message"] == "Articles ingested successfully."
    assert precision >= 0.7 # At least 70% of articles were well classified
