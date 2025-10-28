# app/api/routes.py
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from typing import Dict, Any
import time
import logging
from app.core.engine import StriveCodeEngine
from .schema import (
    CodeTask, GenerateRequest, TranspileRequest, ReconstructRequest,
    UnrestrictedRequest, AIResponse, HealthResponse
)

router = APIRouter(prefix="/api/v1", tags=["Strive-Code AI"])
engine = StriveCodeEngine()
logger = logging.getLogger("strive-code-ai")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """System health and capability probe."""
    return HealthResponse()

@router.post("/task", response_model=AIResponse)
async def execute_task(task: CodeTask, background: BackgroundTasks):
    """
    Universal entrypoint for all Strive-Code AI operations.
    Dispatches to symbolic core engine.
    """
    start_time = time.time()
    action = task.action

    logger.info(f"[API] Task received: {action} | Language: {task.language}")

    try:
        # Normalize input
        payload = task.dict(exclude_unset=True)
        if task.action == "transpile":
            payload["from"] = payload.pop("from_lang", None)
            payload["to"] = payload.pop("to_lang", None)

        # Dispatch to core
        result = engine.process(payload)

        # Enrich response
        elapsed = int((time.time() - start_time) * 1000)

        return AIResponse(
            action=action,
            result=result,
            execution_time_ms=elapsed
        )

    except Exception as e:
        logger.error(f"[API] {action} failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Specialized routes for UX
@router.post("/generate")
async def generate_code(req: GenerateRequest):
    return await execute_task(req)

@router.post("/transpile")
async def transpile_code(req: TranspileRequest):
    return await execute_task(req)

@router.post("/reconstruct")
async def reconstruct_repo(req: ReconstructRequest):
    return await execute_task(req)

@router.post("/unrestricted")
async def unrestricted_generation(req: UnrestrictedRequest):
    return await execute_task(req)

# File download endpoints
@router.get("/download/{file_type}")
async def download_file(file_type: str, task_id: str):
    """Serve generated files: pdf, mp3, ipynb, png"""
    valid = ["pdf", "voice", "notebook", "diagram"]
    if file_type not in valid:
        raise HTTPException(400, "Invalid file type")

    path = f"/tmp/{task_id}.{file_type}"
    if not os.path.exists(path):
        raise HTTPException(404, "File not found")

    return FileResponse(path, media_type=_get_mime(file_type), filename=f"strive_{task_id}.{file_type}")

def _get_mime(ft: str) -> str:
    return {
        "pdf": "application/pdf",
        "mp3": "audio/mpeg",
        "ipynb": "application/x-ipynb+json",
        "png": "image/png"
    }.get(ft, "application/octet-stream")

# Webhook for self-upgrades
@router.post("/webhook/redeploy")
async def redeploy_trigger():
    import subprocess
    subprocess.run(["curl", os.getenv("RENDER_WEBHOOK", "")])
    return {"status": "redeploy_triggered"}
