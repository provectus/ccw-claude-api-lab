"""Tests for PipelineStore and PipelineState."""

import asyncio

import pytest

from app.services.pipeline_store import PipelineState, PipelineStore, UploadRecord


class TestPipelineState:
    async def test_append_event_adds_timestamp(self):
        state = PipelineState(
            id="test-1", status="running", file_paths=[], metadata={}
        )
        await state.append_event({"type": "reasoning", "text": "hello"})
        assert len(state.events) == 1
        assert "timestamp" in state.events[0]
        assert state.events[0]["type"] == "reasoning"

    async def test_append_event_preserves_existing_timestamp(self):
        state = PipelineState(
            id="test-1", status="running", file_paths=[], metadata={}
        )
        await state.append_event({"type": "status", "timestamp": "custom-ts"})
        assert state.events[0]["timestamp"] == "custom-ts"

    async def test_wait_for_events_immediate(self):
        state = PipelineState(
            id="test-1", status="running", file_paths=[], metadata={}
        )
        await state.append_event({"type": "reasoning", "text": "a"})
        await state.append_event({"type": "reasoning", "text": "b"})
        events = await state.wait_for_events(after_index=0, timeout=1.0)
        assert len(events) == 2

    async def test_wait_for_events_after_partial(self):
        state = PipelineState(
            id="test-1", status="running", file_paths=[], metadata={}
        )
        await state.append_event({"type": "reasoning", "text": "a"})
        await state.append_event({"type": "reasoning", "text": "b"})
        events = await state.wait_for_events(after_index=1, timeout=1.0)
        assert len(events) == 1
        assert events[0]["text"] == "b"

    async def test_wait_for_events_timeout(self):
        state = PipelineState(
            id="test-1", status="running", file_paths=[], metadata={}
        )
        events = await state.wait_for_events(after_index=0, timeout=0.1)
        assert events == []

    async def test_wait_notified_by_append(self):
        state = PipelineState(
            id="test-1", status="running", file_paths=[], metadata={}
        )

        async def _append_later():
            await asyncio.sleep(0.05)
            await state.append_event({"type": "complete"})

        asyncio.create_task(_append_later())
        events = await state.wait_for_events(after_index=0, timeout=2.0)
        assert len(events) == 1
        assert events[0]["type"] == "complete"


class TestPipelineStore:
    def test_create_and_get(self):
        store = PipelineStore()
        pipeline = store.create_pipeline(
            file_paths=["/data/file.xlsx"],
            metadata={"deal": "test"},
        )
        assert pipeline.status == "pending"
        assert pipeline.file_paths == ["/data/file.xlsx"]

        fetched = store.get_pipeline(pipeline.id)
        assert fetched is pipeline

    def test_get_nonexistent(self):
        store = PipelineStore()
        assert store.get_pipeline("no-such-id") is None

    def test_list_pipelines(self):
        store = PipelineStore()
        store.create_pipeline(file_paths=["/a.xlsx"])
        store.create_pipeline(file_paths=["/b.xlsx"])
        pipelines = store.list_pipelines()
        assert len(pipelines) == 2
        assert all("id" in p for p in pipelines)


class TestUploadCRUD:
    def test_add_and_get(self):
        store = PipelineStore()
        record = store.add_upload([{"name": "file.xlsx", "path": "/tmp/file.xlsx", "size": 1024}])
        assert isinstance(record, UploadRecord)
        assert len(record.files) == 1

        fetched = store.get_upload(record.id)
        assert fetched is record

    def test_list_uploads(self):
        store = PipelineStore()
        store.add_upload([{"name": "a.xlsx", "path": "/a", "size": 100}])
        store.add_upload([{"name": "b.csv", "path": "/b", "size": 200}])
        assert len(store.list_uploads()) == 2

    def test_delete_upload(self):
        store = PipelineStore()
        record = store.add_upload([{"name": "x.xlsx", "path": "/x", "size": 50}])
        assert store.delete_upload(record.id) is True
        assert store.get_upload(record.id) is None
        assert store.delete_upload("nonexistent") is False
