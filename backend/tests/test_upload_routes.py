"""Tests for upload API routes."""

import io

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.pipeline_store import store


@pytest.fixture(autouse=True)
def clean_store():
    store._pipelines.clear()
    store._uploads.clear()
    yield
    store._pipelines.clear()
    store._uploads.clear()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestUploadRoutes:
    async def test_upload_files(self, client, tmp_path):
        resp = await client.post(
            "/api/uploads",
            files=[
                ("files", ("test.xlsx", b"fake xlsx content", "application/octet-stream")),
            ],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "upload_id" in data
        assert len(data["files"]) == 1
        assert data["files"][0]["name"] == "test.xlsx"

    async def test_list_uploads_empty(self, client):
        resp = await client.get("/api/uploads")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["uploads"] == []

    async def test_list_uploads_with_data(self, client):
        # Upload a file first
        await client.post(
            "/api/uploads",
            files=[("files", ("a.xlsx", b"data", "application/octet-stream"))],
        )
        resp = await client.get("/api/uploads")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    async def test_delete_upload(self, client):
        resp = await client.post(
            "/api/uploads",
            files=[("files", ("b.xlsx", b"data", "application/octet-stream"))],
        )
        upload_id = resp.json()["upload_id"]

        resp = await client.delete(f"/api/uploads/{upload_id}")
        assert resp.status_code == 200
        assert resp.json()["deleted"] is True

        # Verify it's gone
        resp = await client.get("/api/uploads")
        assert resp.json()["total"] == 0

    async def test_delete_nonexistent(self, client):
        resp = await client.delete("/api/uploads/no-such-id")
        assert resp.status_code == 404
