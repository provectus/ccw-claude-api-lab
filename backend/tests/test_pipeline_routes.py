"""Tests for pipeline API routes."""

import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.pipeline_store import PipelineState, store


@pytest.fixture(autouse=True)
def clean_store():
    """Reset the global store between tests."""
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


class TestPipelineRoutes:
    @patch("app.api.routes.pipeline.run_agent", new_callable=AsyncMock)
    async def test_run_pipeline(self, mock_run, client):
        resp = await client.post(
            "/api/pipeline/run",
            json={
                "file_paths": ["/data/test.xlsx"],
                "fund_metadata": {"fund_name": "Test Fund"},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "pipeline_id" in data
        assert data["status"] == "pending"

    async def test_run_pipeline_no_files(self, client):
        resp = await client.post(
            "/api/pipeline/run",
            json={"file_paths": [], "fund_metadata": {}},
        )
        assert resp.status_code == 400

    async def test_get_status_not_found(self, client):
        resp = await client.get("/api/pipeline/no-such-id/status")
        assert resp.status_code == 404

    @patch("app.api.routes.pipeline.run_agent", new_callable=AsyncMock)
    async def test_get_status(self, mock_run, client):
        # Create a pipeline first
        resp = await client.post(
            "/api/pipeline/run",
            json={"file_paths": ["/data/test.xlsx"]},
        )
        pid = resp.json()["pipeline_id"]

        resp = await client.get(f"/api/pipeline/{pid}/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["pipeline_id"] == pid
        assert data["total_steps"] == 4

    async def test_assessment_not_found(self, client):
        resp = await client.get("/api/pipeline/no-such-id/assessment")
        assert resp.status_code == 404

    @patch("app.api.routes.pipeline.run_agent", new_callable=AsyncMock)
    async def test_assessment_not_complete(self, mock_run, client):
        resp = await client.post(
            "/api/pipeline/run",
            json={"file_paths": ["/data/test.xlsx"]},
        )
        pid = resp.json()["pipeline_id"]
        # Pipeline is still pending
        resp = await client.get(f"/api/pipeline/{pid}/assessment")
        assert resp.status_code == 409

    async def test_scenarios(self, client):
        resp = await client.get("/api/pipeline/scenarios")
        assert resp.status_code == 200
        data = resp.json()
        assert "scenarios" in data
        assert len(data["scenarios"]) >= 1
        scenario = data["scenarios"][0]
        assert "file_paths" in scenario
        assert "fund_metadata" in scenario

    @patch("app.api.routes.pipeline.run_agent", new_callable=AsyncMock)
    async def test_run_with_upload_id(self, mock_run, client):
        # Create upload first
        upload_record = store.add_upload([
            {"name": "file.xlsx", "path": "/tmp/file.xlsx", "size": 1024}
        ])
        resp = await client.post(
            "/api/pipeline/run",
            json={"upload_id": upload_record.id},
        )
        assert resp.status_code == 200

    async def test_run_with_invalid_upload(self, client):
        resp = await client.post(
            "/api/pipeline/run",
            json={"upload_id": "nonexistent-upload"},
        )
        assert resp.status_code == 404


class TestSSEStreaming:
    """Test SSE event streaming from the pipeline stream endpoint."""

    @patch("app.api.routes.pipeline.run_agent", new_callable=AsyncMock)
    async def test_sse_format_and_ordering(self, mock_run, client):
        """Verify SSE events arrive in correct format with proper ordering."""
        # Set up a pipeline that will emit known events
        events_to_emit = [
            {"type": "status", "status": "running"},
            {"type": "reasoning", "text": "Analyzing the file..."},
            {"type": "tool_start", "tool": "parse_supplier_feed", "input": {}, "tool_use_id": "tu1", "step_index": 0},
            {"type": "tool_result", "tool": "parse_supplier_feed", "output": {"rows": 100}, "source": "live", "tool_use_id": "tu1", "step_index": 0},
            {"type": "complete", "assessment": None},
        ]

        async def mock_agent_run(pipeline, settings):
            pipeline.status = "running"
            for event in events_to_emit:
                await pipeline.append_event(dict(event))
                await asyncio.sleep(0.01)
            pipeline.status = "completed"

        mock_run.side_effect = mock_agent_run

        # Start pipeline
        resp = await client.post(
            "/api/pipeline/run",
            json={"file_paths": ["/data/test.xlsx"]},
        )
        pid = resp.json()["pipeline_id"]

        # Wait briefly for events to be emitted
        await asyncio.sleep(0.2)

        # Read SSE stream
        async with client.stream("GET", f"/api/pipeline/{pid}/stream") as stream:
            raw_events = []
            async for line in stream.aiter_lines():
                if line.startswith("data:"):
                    data = json.loads(line[len("data:"):].strip())
                    raw_events.append(data)
                    if data.get("type") == "complete":
                        break

        # Verify we got all event types in order
        event_types = [e["type"] for e in raw_events]
        assert "status" in event_types
        assert "reasoning" in event_types
        assert "tool_start" in event_types
        assert "tool_result" in event_types
        assert "complete" in event_types

        # Verify ordering: status comes before tool_start
        assert event_types.index("status") < event_types.index("tool_start")
        # tool_start before tool_result
        assert event_types.index("tool_start") < event_types.index("tool_result")
        # complete is last
        assert event_types[-1] == "complete"

    @patch("app.api.routes.pipeline.run_agent", new_callable=AsyncMock)
    async def test_sse_cursor_replay(self, mock_run, client):
        """Connecting after events are emitted replays all events from start."""
        events = [
            {"type": "status", "status": "running"},
            {"type": "reasoning", "text": "Processing..."},
            {"type": "complete", "assessment": None},
        ]

        async def mock_agent_run(pipeline, settings):
            pipeline.status = "running"
            for event in events:
                await pipeline.append_event(dict(event))
                await asyncio.sleep(0.01)
            pipeline.status = "completed"

        mock_run.side_effect = mock_agent_run

        resp = await client.post(
            "/api/pipeline/run",
            json={"file_paths": ["/data/test.xlsx"]},
        )
        pid = resp.json()["pipeline_id"]

        # Wait for all events to be emitted
        await asyncio.sleep(0.3)

        # Connect after all events — should replay from start
        async with client.stream("GET", f"/api/pipeline/{pid}/stream") as stream:
            raw_events = []
            async for line in stream.aiter_lines():
                if line.startswith("data:"):
                    data = json.loads(line[len("data:"):].strip())
                    raw_events.append(data)
                    if data.get("type") == "complete":
                        break

        assert len(raw_events) == len(events)
        assert raw_events[0]["type"] == "status"
        assert raw_events[-1]["type"] == "complete"

    async def test_stream_not_found(self, client):
        resp = await client.get("/api/pipeline/nonexistent/stream")
        assert resp.status_code == 404
