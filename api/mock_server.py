"""Мок-сервер для разработки frontend."""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/templates")
async def upload_template(file: UploadFile = File(...)):
    return {
        "template_id": "mock-template",
        "design_system": {"patterns": {"title": {}, "content": {}}},
        "confidence": 0.87,
        "patterns_count": 8,
    }


@app.post("/api/content")
async def upload_content(payload: dict):
    return {"content_id": "mock-content", "size": 1234}


@app.post("/api/generate")
async def generate(payload: dict):
    return {"job_id": "mock-job", "status": "processing", "estimated_seconds": 30}


@app.get("/api/jobs/{job_id}")
async def job_status(job_id: str):
    return {
        "job_id": job_id,
        "status": "done",
        "progress": 100,
        "result": {
            "presentations": [
                {"variant_id": 1, "variant_name": "Плотный", "pptx_url": "/files/v1.pptx"},
                {"variant_id": 2, "variant_name": "Акцент на данных", "pptx_url": "/files/v2.pptx"},
                {"variant_id": 3, "variant_name": "Нарративный", "pptx_url": "/files/v3.pptx"},
            ],
            "audit_report": {
                "total_problems": 5,
                "by_severity": {"error": 1, "warning": 3, "info": 1},
                "problems": [
                    {"slide_id": 3, "rule_id": "bounds", "severity": "error", "message": "Элемент вышел за границы"}
                ],
            },
        },
    }


@app.get("/api/models")
async def models():
    return {"models": ["qwen3.8-flash"], "default": "qwen3.8-flash"}


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
