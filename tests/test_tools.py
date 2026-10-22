from __future__ import annotations

import json
import os
from typing import Any

import httpx
import pytest
from crewai.tools.tool_failure import ToolFailure

from decodo_crewai import DecodoSearchTool, DecodoWebScraperTool


class FakeApi:
    """Stands in for httpx.request inside the SDK and records what was sent."""

    def __init__(self, status_code: int = 200, body: Any = None) -> None:
        self.status_code = status_code
        self.body = body if body is not None else {"results": [{"content": "# Hello", "status_code": 200}]}
        self.calls: list[dict[str, Any]] = []

    def __call__(self, method: str, url: str, *, headers: dict[str, str], json: Any, timeout: float) -> httpx.Response:
        self.calls.append({"method": method, "url": url, "headers": headers, "json": json})
        return httpx.Response(self.status_code, json=self.body)

    @property
    def payload(self) -> dict[str, Any]:
        return self.calls[-1]["json"]  # type: ignore[no-any-return]


@pytest.fixture
def fake_api(monkeypatch: pytest.MonkeyPatch) -> FakeApi:
    api = FakeApi()
    monkeypatch.setattr("decodo.http.httpx.request", api)
    return api


@pytest.fixture(autouse=True)
def _api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DECODO_API_KEY", "test-key")


def test_missing_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DECODO_API_KEY")
    with pytest.raises(ValueError, match="DECODO_API_KEY"):
        DecodoWebScraperTool()


def test_api_key_argument_overrides_env(fake_api: FakeApi) -> None:
    DecodoWebScraperTool(api_key="explicit-key").run(url="https://example.com")
    assert fake_api.calls[0]["headers"]["Authorization"] == "Bearer explicit-key"


def test_requests_go_to_data_api_with_crewai_integration_header(fake_api: FakeApi) -> None:
    DecodoWebScraperTool().run(url="https://example.com")

    call = fake_api.calls[0]
    assert call["url"].startswith("https://data.decodo.com/")
    assert call["headers"]["Authorization"] == "Bearer test-key"
    assert call["headers"]["x-integration"] == "crewai-python"


def test_web_scraper_returns_markdown(fake_api: FakeApi) -> None:
    result = DecodoWebScraperTool().run(url="https://example.com")

    assert result == "# Hello"
    assert fake_api.payload == {"target": "universal", "url": "https://example.com", "markdown": True}


def test_web_scraper_js_render_and_geo(fake_api: FakeApi) -> None:
    DecodoWebScraperTool().run(url="https://example.com", js_render=True, geo="Germany")

    assert fake_api.payload["headless"] == "html"
    assert fake_api.payload["geo"] == "Germany"


def test_web_scraper_truncates_long_pages(fake_api: FakeApi) -> None:
    fake_api.body = {"results": [{"content": "a" * 50, "status_code": 200}]}

    result = DecodoWebScraperTool(max_chars=10).run(url="https://example.com")

    assert result.startswith("a" * 10 + "\n\n[Truncated to 10 of 50 characters.]")


def test_search_google_returns_full_parsed_results(fake_api: FakeApi) -> None:
    content = {"results": {"organic": [{"title": "A", "images": ["x"]}], "images": ["y"]}}
    fake_api.body = {"results": [{"status_code": 200, "content": content}]}

    result = DecodoSearchTool().run(query="coffee")

    assert fake_api.payload == {"target": "google_search", "query": "coffee", "parse": True}
    assert json.loads(result) == content


def test_search_amazon(fake_api: FakeApi) -> None:
    content = {"results": {"organic": [], "suggested": [1]}}
    fake_api.body = {"results": [{"status_code": 200, "content": content}]}

    result = DecodoSearchTool().run(query="keyboard", source="amazon", geo="United States")

    assert fake_api.payload == {"target": "amazon_search", "query": "keyboard", "geo": "United States", "parse": True}
    assert json.loads(result) == content


@pytest.mark.parametrize(
    ("status_code", "code", "retryable"),
    [
        (401, "authentication_failed", False),
        (422, "invalid_params", False),
        (429, "rate_limited", True),
        (500, "500", True),
    ],
)
def test_api_errors_become_tool_failures(fake_api: FakeApi, status_code: int, code: str, retryable: bool) -> None:
    fake_api.status_code = status_code
    fake_api.body = {"message": "nope"}

    result = DecodoWebScraperTool()._run(url="https://example.com")

    assert isinstance(result, ToolFailure)
    assert result.code == code
    assert result.retryable is retryable


def test_target_error_status_becomes_tool_failure(fake_api: FakeApi) -> None:
    fake_api.body = {"results": [{"content": "", "status_code": 404}]}

    result = DecodoWebScraperTool()._run(url="https://example.com/missing")

    assert isinstance(result, ToolFailure)
    assert result.code == "404"


def test_empty_results_become_tool_failure(fake_api: FakeApi) -> None:
    fake_api.body = {"results": []}

    result = DecodoSearchTool()._run(query="coffee")

    assert isinstance(result, ToolFailure)
    assert result.code == "empty_response"


@pytest.mark.live
@pytest.mark.skipif(not os.environ.get("DECODO_LIVE_API_KEY"), reason="DECODO_LIVE_API_KEY not set")
def test_live_scrape_and_search() -> None:
    api_key = os.environ["DECODO_LIVE_API_KEY"]

    page = DecodoWebScraperTool(api_key=api_key).run(url="https://ip.decodo.com")
    assert isinstance(page, str) and page

    results = DecodoSearchTool(api_key=api_key).run(query="decodo")
    assert isinstance(results, str) and json.loads(results)
