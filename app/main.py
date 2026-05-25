from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.backend_client import BackendClient
from app.models import ReportRequest
from app.generators import generate_summary_report, generate_short_report, generate_full_report

app = FastAPI(title="Test Report Generator")
backend = BackendClient()
@app.get("/")
async def root():
    return {"message": "Generator is alive", "status": "ok"}
@app.get("/health")
async def health():
    return {"status": "healthy"}
@app.post("/generate_report")
async def generate_report(request: ReportRequest):
    try:
        print(f"Получен запрос: run_id={request.run_id}, template_type={request.template_type}")

        test_data = await backend.get_test_run_data(request.run_id)

        print(f"Данные получены: проект={test_data.project_name}")

        if request.template_type == "summary":
            filepath = generate_summary_report(test_data)
        elif request.template_type == "short":
            filepath = generate_short_report(test_data)
        elif request.template_type == "full":
            filepath = generate_full_report(test_data)
        else:
            raise HTTPException(400, f"Неизвестный тип шаблона: {request.template_type}")

        print(f"Отчёт сгенерирован: {filepath}")

        return FileResponse(
            path=filepath,
            filename=filepath.split("/")[-1],
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(500, detail=str(e))