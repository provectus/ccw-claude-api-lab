"""Pipeline execution endpoints."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.api.deps import get_settings
from app.services.agent_runner import run_agent
from app.services.pipeline_store import store

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


class PipelineRunRequest(BaseModel):
    file_paths: list[str] = []
    upload_id: str | None = None
    fund_metadata: dict = {}


@router.post("/run")
async def run_pipeline(request: PipelineRunRequest):
    """Start a new pipeline execution."""
    settings = get_settings()
    file_paths = list(request.file_paths)

    # Resolve file paths from upload_id if provided
    if request.upload_id:
        upload = store.get_upload(request.upload_id)
        if upload is None:
            raise HTTPException(status_code=404, detail="Upload not found")
        file_paths.extend(f["path"] for f in upload.files)

    if not file_paths:
        raise HTTPException(status_code=400, detail="No files provided")

    pipeline = store.create_pipeline(
        file_paths=file_paths,
        metadata=request.fund_metadata,
    )

    # Launch agent as background task, store reference to prevent GC
    task = asyncio.create_task(run_agent(pipeline, settings))
    pipeline._task = task

    return {
        "pipeline_id": pipeline.id,
        "status": pipeline.status,
        "created_at": pipeline.created_at,
    }


@router.get("/list")
async def list_pipelines():
    """List all pipeline runs with summary info."""
    pipelines = store.list_pipelines()
    pipelines.sort(key=lambda p: p["created_at"], reverse=True)
    return {"pipelines": pipelines}


@router.get("/{pipeline_id}/events")
async def get_pipeline_events(pipeline_id: str):
    """Get all events for a pipeline (for historical replay)."""
    pipeline = store.get_pipeline(pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {
        "pipeline_id": pipeline.id,
        "status": pipeline.status,
        "events": pipeline.events,
        "metadata": pipeline.metadata,
    }


@router.get("/{pipeline_id}/stream")
async def stream_pipeline(pipeline_id: str):
    """Stream pipeline execution events via SSE."""
    pipeline = store.get_pipeline(pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    async def event_generator():
        cursor = 0
        while True:
            events = await pipeline.wait_for_events(after_index=cursor, timeout=30.0)
            for event in events:
                yield {
                    "event": event.get("type", "message"),
                    "data": json.dumps(event),
                }
                cursor += 1

            # Stop streaming after terminal states
            if pipeline.status in ("completed", "failed"):
                break

    return EventSourceResponse(
        event_generator(),
        headers={"X-Accel-Buffering": "no"},
    )


@router.get("/{pipeline_id}/status")
async def get_pipeline_status(pipeline_id: str):
    """Get current pipeline status."""
    pipeline = store.get_pipeline(pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    tool_results = [e for e in pipeline.events if e.get("type") == "tool_result"]
    return {
        "pipeline_id": pipeline.id,
        "status": pipeline.status,
        "steps_completed": len(tool_results),
        "total_steps": 4,
        "event_count": len(pipeline.events),
        "created_at": pipeline.created_at,
        "completed_at": pipeline.completed_at,
    }


@router.get("/{pipeline_id}/assessment")
async def get_pipeline_assessment(pipeline_id: str):
    """Get the deal assessment result for a completed pipeline."""
    pipeline = store.get_pipeline(pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    if pipeline.status not in ("completed", "failed"):
        raise HTTPException(status_code=409, detail="Pipeline not yet complete")

    # Collect narrative from reasoning events
    reasoning_texts = [
        e["text"] for e in pipeline.events if e.get("type") == "reasoning"
    ]

    # Collect tool outputs so the frontend can render charts without store events
    tool_outputs: dict = {}
    for e in pipeline.events:
        if e.get("type") == "tool_result" and e.get("tool"):
            tool_outputs[e["tool"]] = e.get("output")

    return {
        "pipeline_id": pipeline.id,
        "status": pipeline.status,
        "assessment": pipeline.assessment,
        "narrative": reasoning_texts,
        "tool_outputs": tool_outputs,
    }


@router.get("/scenarios", include_in_schema=True)
async def get_scenarios():
    """Return pre-configured demo PA requests with folder paths to sample data."""
    settings = get_settings()
    sample = settings.sample_data_dir

    return {
        "scenarios": [
            {
                "id": "lumbar_mri",
                "name": "Lumbar MRI (72148) — meets policy",
                "description": (
                    "MRI lumbar spine for chronic low-back pain with 8 weeks conservative "
                    "treatment, completed PT, and prior imaging. Clean approve case."
                ),
                "file_paths": [str(sample / "lumbar_mri")],
                "fund_metadata": {
                    "request_id": "PA-2026-0413",
                    "cpt_code": "72148",
                    "plan_type": "PPO",
                },
            },
            {
                "id": "knee_arthroscopy",
                "name": "Knee Arthroscopy (29881) — criteria unmet",
                "description": (
                    "Knee arthroscopy with imaging-confirmed meniscal tear, but only 3 weeks of "
                    "conservative treatment and no documented PT. Should pend for more info."
                ),
                "file_paths": [str(sample / "knee_arthroscopy")],
                "fund_metadata": {
                    "request_id": "PA-2026-0511",
                    "cpt_code": "29881",
                    "plan_type": "HMO",
                },
            },
            {
                "id": "incomplete_request",
                "name": "Brain MRI (70553) — incomplete request",
                "description": (
                    "Brain MRI request missing the primary diagnosis and several clinical "
                    "fields — exercises the validation / pend-for-info path."
                ),
                "file_paths": [str(sample / "incomplete_request")],
                "fund_metadata": {
                    "request_id": "PA-2026-0522",
                    "cpt_code": "70553",
                    "plan_type": "Medicare Advantage",
                },
            },
        ]
    }
