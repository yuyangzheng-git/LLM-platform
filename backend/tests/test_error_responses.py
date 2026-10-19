"""
Error responses must not leak raw exception text to clients, and
intentional HTTP errors (404/400) must not be turned into 500s.
"""
import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app


def test_chat_completion_unknown_conversation_is_404():
    with TestClient(app) as client:
        resp = client.post(
            "/api/v1/chat/complete",
            json={"conversation_id": 999999, "message": "hi"},
        )
    assert resp.status_code == 404


def test_docs_disabled_when_not_debug():
    with TestClient(app) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404
