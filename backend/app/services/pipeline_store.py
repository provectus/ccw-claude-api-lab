"""In-memory store for pipeline state and upload records."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class UploadRecord:
    id: str
    files: list[dict]  # [{name, path, size}]
    created_at: str


@dataclass
class PipelineState:
    id: str
    status: str  # pending | running | completed | failed
    file_paths: list[str]
    metadata: dict
    events: list[dict] = field(default_factory=list)
    assessment: dict | None = None
    error: str | None = None
    created_at: str = ""
    completed_at: str | None = None
    _condition: asyncio.Condition = field(
        default_factory=asyncio.Condition, repr=False
    )
    _task: asyncio.Task | None = field(default=None, repr=False)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    async def append_event(self, event: dict) -> None:
        """Append event and notify any SSE waiters."""
        if "timestamp" not in event:
            event["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.events.append(event)
        async with self._condition:
            self._condition.notify_all()

    async def wait_for_events(self, after_index: int, timeout: float = 30.0) -> list[dict]:
        """Block until new events arrive after the given index, or timeout."""
        async with self._condition:
            # Check if events already available
            if after_index < len(self.events):
                return self.events[after_index:]
            # Wait for notification
            try:
                await asyncio.wait_for(
                    self._condition.wait(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                pass
            return self.events[after_index:]


class PipelineStore:
    """In-memory store for pipeline runs and uploads."""

    def __init__(self):
        self._pipelines: dict[str, PipelineState] = {}
        self._uploads: dict[str, UploadRecord] = {}

    # --- Pipeline CRUD ---

    def create_pipeline(
        self,
        file_paths: list[str],
        metadata: dict | None = None,
    ) -> PipelineState:
        pipeline_id = str(uuid.uuid4())
        pipeline = PipelineState(
            id=pipeline_id,
            status="pending",
            file_paths=file_paths,
            metadata=metadata or {},
        )
        self._pipelines[pipeline_id] = pipeline
        return pipeline

    def get_pipeline(self, pipeline_id: str) -> PipelineState | None:
        return self._pipelines.get(pipeline_id)

    def list_pipelines(self) -> list[dict]:
        results = []
        for p in self._pipelines.values():
            summary: dict = {
                "id": p.id,
                "status": p.status,
                "created_at": p.created_at,
                "completed_at": p.completed_at,
                "event_count": len(p.events),
                "fund_name": p.metadata.get("fund_name", "Unknown Fund"),
                "fund_type": p.metadata.get("fund_type", ""),
                "recommendation": None,
                "data_quality_score": None,
            }
            if p.assessment:
                summary["recommendation"] = p.assessment.get("recommendation")
                es = p.assessment.get("executive_summary", {})
                if isinstance(es, dict):
                    summary["data_quality_score"] = es.get("data_quality_score")
            results.append(summary)
        return results

    # --- Upload CRUD ---

    def add_upload(self, files: list[dict]) -> UploadRecord:
        upload_id = str(uuid.uuid4())
        record = UploadRecord(
            id=upload_id,
            files=files,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._uploads[upload_id] = record
        return record

    def get_upload(self, upload_id: str) -> UploadRecord | None:
        return self._uploads.get(upload_id)

    def list_uploads(self) -> list[UploadRecord]:
        return list(self._uploads.values())

    def delete_upload(self, upload_id: str) -> bool:
        return self._uploads.pop(upload_id, None) is not None


# Module-level singleton
store = PipelineStore()
