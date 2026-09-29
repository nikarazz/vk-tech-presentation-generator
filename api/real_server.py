"""Реальный backend для генератора презентаций.

Использует pipeline (parser -> plan -> variants -> export).
"""
import uuid
import shutil
import traceback
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from parser.parse_template import parse_template
from generation.plan_content import plan_content_stub
from generation.variants import generate_variants
from generation.export.export_pptx import export_pptx
from generation.export.export_pdf import export_pdf
from generation.export.export_html import export_html


app = FastAPI(title="Presentation Generator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORAGE = Path("api/storage")
STORAGE.mkdir(parents=True, exist_ok=True)
(STORAGE / "templates").mkdir(exist_ok=True)
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

templates_db = {}
content_db = {}
jobs_db = {}


class ContentPack(BaseModel):
    content_pack: dict


class GenerateRequest(BaseModel):
    template_id: str
    content_id: str
    brief: str
    variants: int = 3


@app.get("/")
def root():
    return {"status": "ok", "service": "presentation-generator"}


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/templates")
async def upload_template(file: UploadFile = File(...)):
    """Загружает .pptx, парсит, сохраняет ОРИГИНАЛЬНОЕ имя."""
    template_id = str(uuid.uuid4())[:8]
    original_name = file.filename or "template.pptx"

    # Сохраняем с оригинальным именем — чтобы _pick_text_color видел шаблон
    safe_name = (
        original_name
        .replace(" ", "_")
        .replace("\\", "_")
        .replace("/", "_")
    )
    path = STORAGE / "templates" / f"{template_id}_{safe_name}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        ds = parse_template(str(path))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(400, f"Parse failed: {e}")

    # ★ Прокидываем ОРИГИНАЛЬНОЕ имя в meta
    ds["meta"]["source_file"] = original_name
    ds["meta"]["original_filename"] = original_name

    templates_db[template_id] = {
        "path": str(path),
        "ds": ds,
        "name": original_name,
    }

    return {
        "template_id": template_id,
        "design_system": {
            "palette": ds.get("palette", {}),
            "typography": ds.get("typography", {}),
            "patterns": list(ds.get("patterns", {}).keys()),
        },
        "confidence": ds.get("meta", {}).get("confidence", 0.0),
        "patterns_count": len(ds.get("patterns", {})),
    }


@app.post("/api/content")
async def upload_content(payload: ContentPack):
    content_id = str(uuid.uuid4())[:8]
    content_db[content_id] = payload.content_pack
    return {"content_id": content_id, "size": len(payload.content_pack)}


@app.post("/api/generate")
async def generate(req: GenerateRequest, background: BackgroundTasks):
    if req.template_id not in templates_db:
        raise HTTPException(404, "Template not found")
    if req.content_id not in content_db:
        raise HTTPException(404, "Content not found")

    job_id = str(uuid.uuid4())[:8]
    jobs_db[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "progress": 0,
        "stage": "queued",
        "message": "Task created",
        "result": None,
        "error": None,
    }

    background.add_task(_run_job, job_id, req.template_id, req.brief)
    return {"job_id": job_id, "status": "processing", "estimated_seconds": 60}


@app.get("/api/jobs/{job_id}")
async def job_status(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(404, "Job not found")
    return jobs_db[job_id]


@app.get("/api/files/{filename}")
async def get_file(filename: str):
    path = OUTPUT / filename
    if not path.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(str(path), filename=filename)


@app.get("/api/models")
async def models():
    return {"models": ["qwen3.8-flash"], "default": "qwen3.8-flash"}


def _run_job(job_id: str, template_id: str, brief: str):
    job = jobs_db[job_id]
    try:
        job.update(progress=10, stage="parsing", message="Parsing template...")
        template_path = templates_db[template_id]["path"]
        ds = templates_db[template_id]["ds"]
        # ★ source_file уже установлен в оригинальное имя

        job.update(progress=30, stage="planning", message="Planning content...")
        plan = plan_content_stub(brief, {}, ds)

        job.update(progress=50, stage="layout", message="Layout slides...")
        variants = generate_variants(plan, ds)

        job.update(progress=70, stage="export", message="Export files...")
        presentations = []
        for i, (vname, pres) in enumerate(variants.items(), 1):
            pptx_name = f"{job_id}_{vname}.pptx"
            pptx_path = OUTPUT / pptx_name
            export_pptx(pres, ds, template_path, str(pptx_path))

            pdf_url = None
            html_url = None
            try:
                pdf_path = OUTPUT / f"{job_id}_{vname}.pdf"
                export_pdf(str(pptx_path), str(pdf_path))
                pdf_url = f"/api/files/{job_id}_{vname}.pdf"
            except Exception as e:
                print(f"[pdf] {vname}: {e}")
            try:
                html_path = OUTPUT / f"{job_id}_{vname}.html"
                export_html(str(pptx_path), str(html_path))
                html_url = f"/api/files/{job_id}_{vname}.html"
            except Exception as e:
                print(f"[html] {vname}: {e}")

            presentations.append({
                "variant_id": i,
                "variant_name": vname,
                "pptx_url": f"/api/files/{pptx_name}",
                "pdf_url": pdf_url,
                "html_url": html_url,
            })

        audit_report = {
            "total_problems": 0,
            "by_severity": {"error": 0, "warning": 0, "info": 0},
            "problems": [],
        }

        job.update(
            status="done",
            progress=100,
            stage="done",
            message="Done",
            result={
                "presentations": presentations,
                "audit_report": audit_report,
            },
        )
        print(f"[job {job_id}] DONE: {len(presentations)} variants")

    except Exception as e:
        traceback.print_exc()
        job.update(status="error", progress=100, stage="error", error=str(e))