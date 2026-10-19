"""
Upload handling: streamed to disk, size limit enforced without buffering
the whole body, and file type decided by extension rather than the
client-supplied Content-Type.
"""
import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings
from app.main import app


def _upload(client, name, data, content_type):
    return client.post(
        "/api/v1/files/upload",
        files={"file": (name, data, content_type)},
    )


def test_text_upload_is_processed_by_extension():
    with TestClient(app) as client:
        resp = _upload(client, "notes.txt", b"hello world", "application/octet-stream")
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["mime_type"] == "text/plain"
    assert body["file_type"] == "text"


def test_svg_is_rejected():
    with TestClient(app) as client:
        resp = _upload(client, "x.svg", b"<svg onload='alert(1)'/>", "image/svg+xml")
    assert resp.status_code == 400


def test_oversized_upload_is_rejected_and_not_left_on_disk(monkeypatch):
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 1024)
    before = set(os.listdir(settings.UPLOAD_DIR))
    with TestClient(app) as client:
        resp = _upload(client, "big.txt", b"a" * 4096, "text/plain")
    assert resp.status_code == 400
    assert "超过限制" in resp.json()["detail"]
    assert set(os.listdir(settings.UPLOAD_DIR)) == before


def test_invalid_utf8_text_still_uploads():
    with TestClient(app) as client:
        resp = _upload(client, "latin1.txt", "café".encode("latin-1"), "text/plain")
    assert resp.status_code == 201, resp.text
