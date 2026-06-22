# Report Generator

Микросервис для генерации отчётов по тестированию.

## Запуск

pip install -r requirements.txt

python run.py

## Развёртывание
docker-compose up --build

## API

POST /generate
Content-Type: application/json

{
  "run_id": "ID_прогона",
  "template_type": "summary|short|full",
  "jwt_token": "токен_пользователя"
}

## Переменные окружения

BACKEND_URL - URL бэкенда (по умолчанию http://localhost:8080)
