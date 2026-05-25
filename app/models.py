from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime


class TestStatus(str, Enum):
    SUCCESS = "Успешно"
    ERROR = "С ошибкой"
    SKIPPED = "Пропущен"


class TestCaseDetail(BaseModel):
    name: str
    status: TestStatus
    duration: str


class DefectStep(BaseModel):
    test_case_id: str
    step_number: int
    description: str


class TestRunData(BaseModel):
    """Данные для сводного отчёта (Шаблон 1)"""
    # Основная информация
    project_name: str
    version: str
    run_name: str
    run_version: str

    # Метрики
    total_tests: int
    successful_tests: int
    failed_tests: int
    skipped_tests: int
    error_percentage: float
    skipped_percentage: float

    # Дефекты и ошибки
    has_blocking_defect: bool = False
    blocking_defect: Optional[DefectStep] = None

    failed_test_cases: List[DefectStep] = []  # тест-кейсы с ошибками
    skipped_test_cases: List[DefectStep] = []  # пропущенные тест-кейсы

    critical_errors: List[DefectStep] = []  # критические ошибки (с галочкой)
    non_critical_errors: List[DefectStep] = []  # некритические ошибки

    # Данные для таблицы в приложении
    test_cases_table: List[TestCaseDetail] = []

    # Подписи
    responsible_person: str
    initiator_name: str

    # Дата и время прогона
    run_datetime: datetime = Field(default_factory=datetime.now)

class ReportRequest(BaseModel):
    """Запрос от фронтенда на генерацию отчёта"""
    run_id: str
    template_type: str  # "summary", "short", "full"