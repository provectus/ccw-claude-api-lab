"""Dashboard statistics endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.services.pipeline_store import store

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
async def get_stats():
    """Get dashboard statistics computed from pipeline store."""
    pipelines = store.list_pipelines()
    completed = [p for p in pipelines if p["status"] == "completed"]

    # Count files processed across all pipelines
    files_processed = 0
    records_validated = 0
    total_completion_seconds = 0.0

    for p_summary in pipelines:
        pipeline = store.get_pipeline(p_summary["id"])
        if pipeline is None:
            continue
        files_processed += len(pipeline.file_paths)

        for event in pipeline.events:
            # Count diagnoses parsed from parse_pa_request results
            if (
                event.get("type") == "tool_result"
                and event.get("tool") == "parse_pa_request"
                and isinstance(event.get("output"), dict)
            ):
                records_validated += event["output"].get("diagnosis_count", 0)

    # Average completion time for completed pipelines
    avg_seconds = 0.0
    if completed:
        from datetime import datetime

        for p_summary in completed:
            pipeline = store.get_pipeline(p_summary["id"])
            if pipeline and pipeline.completed_at:
                try:
                    start = datetime.fromisoformat(pipeline.created_at)
                    end = datetime.fromisoformat(pipeline.completed_at)
                    total_completion_seconds += (end - start).total_seconds()
                except (ValueError, TypeError):
                    pass
        avg_seconds = total_completion_seconds / len(completed) if completed else 0.0

    last_run = None
    if pipelines:
        last_run = max(p["created_at"] for p in pipelines)

    return {
        "pipelines_run": len(pipelines),
        "pipelines_completed": len(completed),
        "files_processed": files_processed,
        "records_validated": records_validated,
        "avg_completion_time_seconds": round(avg_seconds, 1),
        "last_run": last_run,
    }
