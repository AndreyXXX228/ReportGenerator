# Test Report Generator

Микросервис для генерации отчётов по тестированию (3 шаблона).

## Запуск

pip install -r requirements.txt

python run.py

## API

POST /generate
Content-Type: application/json

{
"run_id": "run-001",
"template_type": "summary" # summary / short / full
}

## Переменные окружения

BACKEND_URL - URL бэкенда (по умолчанию http://localhost:8080)