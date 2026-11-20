import os

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.platforms.base import BasePlatform
from app.services import posting_service

VALID_MESSAGE = (
    "Check out our latest business platform and grow your online "
    "visibility. https://example.com"
)
client = TestClient(app)


class FakePlatform(BasePlatform):
    def __init__(self, name: str, url: str | None = None, error: str | None = None):
        self.name = name
        self.url = url
        self.error = error

    def post(self, message: str, client) -> str:
        if self.error:
            raise RuntimeError(self.error)
        return self.url


@pytest.fixture
def use_platforms(monkeypatch):
    def install(platforms):
        monkeypatch.setattr(posting_service, "build_platforms", lambda: platforms)

    return install


def test_posting_continues_after_failure(use_platforms):
    use_platforms(
        [
            FakePlatform("Platform A", "https://example.com/post/123"),
            FakePlatform("Platform B", error="Authentication failed"),
            FakePlatform("Platform C", "https://example.com/post/456"),
        ]
    )
    response = client.post("/posting", json={"message": VALID_MESSAGE})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert [result["status"] for result in body["results"]] == [
        "success",
        "failed",
        "success",
    ]
    failed = body["results"][1]
    assert failed["posted_url"] is None
    assert failed["public_access"] is False
    assert failed["error"] == "RuntimeError: Authentication failed"
    assert body["results"][0]["posted_url"] == "https://example.com/post/123"
    assert body["results"][0]["date"] and body["results"][0]["time"]


def test_all_failures_returns_success_false(use_platforms):
    use_platforms([FakePlatform("Platform A", error="timeout")])
    body = client.post("/posting", json={"message": VALID_MESSAGE}).json()
    assert body["success"] is False


@pytest.mark.parametrize(
    "message",
    [
        "",
        "a" * 201 + " https://example.com",
        "No link in this message",
        "https://example.com and https://example.org",
        "Visit https://",
    ],
)
def test_invalid_messages_are_rejected(use_platforms, message):
    use_platforms([FakePlatform("Platform A", "https://example.com/1")])
    response = client.post("/posting", json={"message": message})
    assert response.status_code == 422
    assert response.json()["success"] is False


def test_trailing_punctuation_after_link_is_accepted(use_platforms):
    use_platforms([FakePlatform("Platform A", "https://example.com/1")])
    response = client.post("/posting", json={"message": "See https://example.com."})
    assert response.status_code == 200
    assert response.json()["results"][0]["status"] == "success"


@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="live API test")
def test_live_posting():
    body = client.post("/posting", json={"message": VALID_MESSAGE}).json()
    assert body["success"] is True
    assert sum(r["status"] == "success" for r in body["results"]) >= 5
