import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.backend_client import BackendClient
from app.generators import (
    generate_full_report,
    generate_pdf_report,
    generate_short_report,
    generate_summary_report,
)
from app.models import ReportRequest

load_dotenv()

app = FastAPI(title="Test Report Generator")

_cors_origins = os.getenv("CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if _cors_origins.strip() == "*" else [o.strip() for o in _cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backend = BackendClient()
@app.get("/")
async def root():
    return {"message": "Generator is alive", "status": "ok"}
@app.get("/health")
async def health():
    return {"status": "healthy"}
@app.post("/generate_report")
async def generate_report(request: ReportRequest):
    test_data = await backend.get_test_run_data(request.run_id, request.jwt_token)

    if request.template_type == "summary":
        filepath = generate_summary_report(test_data)
    elif request.template_type == "short":
        filepath = generate_short_report(test_data)
    elif request.template_type == "full":
        filepath = generate_full_report(test_data)
    elif request.template_type == "pdf":
        filepath = generate_pdf_report(test_data)
    else:
        raise HTTPException(400, f"Неизвестный тип шаблона: {request.template_type}")

    media_type = "application/pdf" if request.template_type == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return FileResponse(
        path=filepath,
        filename=os.path.basename(filepath),
        media_type=media_type
    )