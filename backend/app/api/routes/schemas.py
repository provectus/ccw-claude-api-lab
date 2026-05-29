"""Schema retrieval endpoints."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/schemas", tags=["schemas"])

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"


@router.get("")
async def list_schemas():
    """List available schemas."""
    schemas = []
    if SCHEMAS_DIR.exists():
        for f in sorted(SCHEMAS_DIR.glob("*.json")):
            schemas.append({"name": f.stem, "filename": f.name})
    return {"schemas": schemas}


@router.get("/{name}")
async def get_schema(name: str):
    """Get a specific schema by name."""
    path = SCHEMAS_DIR / f"{name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Schema '{name}' not found")
    return json.loads(path.read_text())
