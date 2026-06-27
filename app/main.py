from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import py_eureka_client.eureka_client as eureka_client

from app.models import ReportRequest
from app.generators import generate_summary_report, generate_short_report, generate_full_report
from app.backend_client import BackendClient

@asynccontextmanager
async def lifespan(_app: FastAPI):
    print("Приложение запускается...")
    eureka_server = os.getenv("EUREKA_SERVER_URL", "http://eureka:8761/eureka")
    service_name = os.getenv("SERVICE_NAME", "report-generator")
    service_port = int(os.getenv("PORT", 8000))


    use_eureka = os.getenv("USE_EUREKA", "true").lower() == "true"
    if use_eureka:
        try:
            await eureka_client.init_async(
                eureka_server=eureka_server,
                app_name=service_name,
                instance_port=service_port,
                instance_host="report-generator"
            )
            print(f"Успешно зарегистрировался в Eureka: {eureka_server}")
        except Exception as e:
            print(f"Ошибка регистрации в Eureka: {e}")
    else:
        print("Регистрация в Eureka отключена (USE_EUREKA=false)")

    yield

    print("Приложение останавливается...")
    if use_eureka:
        try:
            await eureka_client.stop_async()
            print("Отключился от Eureka")
        except Exception as e:
            print(f"Ошибка отключения от Eureka: {e}")

app = FastAPI(
    title="Report Generator",
    description="Микросервис для генерации отчетов по тестированию",
    lifespan=lifespan
)

backend = BackendClient()

# --- Эндпоинты ---
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

        if request.template_type == "summary":
            filepath = generate_summary_report(test_data)
        elif request.template_type == "short":
            filepath = generate_short_report(test_data)
        elif request.template_type == "full":
            filepath = generate_full_report(test_data)
        else:
            raise HTTPException(400, f"Неизвестный тип шаблона: {request.template_type}")

        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(500, detail=str(e))