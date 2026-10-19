"""
Tests for the SSRF guard used by the web scraper tool.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.url_guard import UnsafeURLError, assert_public_url
from app.tools.web_scraper_tool import analyze_website


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "http://localhost:3211/health",
        "http://10.0.0.5/",
        "http://192.168.1.1/",
        "http://172.17.0.1/",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/",
        "http://[::ffff:127.0.0.1]/",
        "http://0.0.0.0/",
        "file:///etc/passwd",
        "ftp://example.com/",
    ],
)
async def test_rejects_internal_or_non_http_urls(url):
    with pytest.raises(UnsafeURLError):
        await assert_public_url(url)


async def test_accepts_public_ip_literal():
    await assert_public_url("https://1.1.1.1/")


async def test_analyze_website_refuses_internal_url():
    result = await analyze_website("http://127.0.0.1:3211/health")
    assert result["success"] is False
    assert "内网" in result["error"]


async def test_redirect_to_internal_address_is_blocked(monkeypatch):
    import httpx
    from app.tools import web_scraper_tool

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "http://169.254.169.254/"})

    real_client = httpx.AsyncClient

    def fake_client(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return real_client(*args, **kwargs)

    monkeypatch.setattr(web_scraper_tool.httpx, "AsyncClient", fake_client)
    result = await analyze_website("https://1.1.1.1/")
    assert result["success"] is False
    assert "内网" in result["error"]
