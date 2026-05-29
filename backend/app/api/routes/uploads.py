"""File upload endpoints."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.api.deps import get_settings
from app.services.pipeline_store import store

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("")
async def upload_files(files: list[UploadFile]):
    """Upload files for pipeline processing."""
    settings = get_settings()
    upload_id = str(uuid.uuid4())
    upload_dir = Path(settings.upload_dir) / upload_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_records = []
    for f in files:
        dest = upload_dir / f.filename
        with dest.open("wb") as out:
            content = await f.read()
            out.write(content)
        file_records.append({
            "name": f.filename,
            "path": str(dest),
            "size": len(content),
        })

    record = store.add_upload(file_records)
    # Re-key with our upload_id so the disk paths match the store key
    old_id = record.id
    record.id = upload_id
    store._uploads.pop(old_id, None)
    store._uploads[upload_id] = record

    return {
        "upload_id": record.id,
        "files": record.files,
        "created_at": record.created_at,
    }


@router.get("")
async def list_uploads():
    """List all uploaded file sets."""
    uploads = store.list_uploads()
    return {
        "uploads": [
            {"id": u.id, "files": u.files, "created_at": u.created_at}
            for u in uploads
        ],
        "total": len(uploads),
    }


@router.delete("/{upload_id}")
async def delete_upload(upload_id: str):
    """Delete an uploaded file set and its files on disk."""
    settings = get_settings()
    upload = store.get_upload(upload_id)
    if upload is None:
        raise HTTPException(status_code=404, detail="Upload not found")

    # Remove files from disk
    upload_dir = Path(settings.upload_dir) / upload_id
    if upload_dir.exists():
        shutil.rmtree(upload_dir)

    store.delete_upload(upload_id)
    return {"upload_id": upload_id, "deleted": True}
