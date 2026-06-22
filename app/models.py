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
    # Основная информация (приходит с бэка)
    project_name: str
    project_description: str = ""
    version: str
    run_name: str
    run_version: str
    run_description: str = ""
    start_datetime: datetime = Field(default_factory=datetime.now)
    end_datetime: datetime = Field(default_factory=datetime.now)

    # Единственный источник метрик — таблица тест-кейсов
    test_cases_table: List[TestCaseDetail] = []

    # Дефекты
    blocking_defect: Optional[DefectStep] = None
    failed_test_cases: List[DefectStep] = []
    skipped_test_cases: List[DefectStep] = []
    critical_errors: List[DefectStep] = []
    non_critical_errors: List[DefectStep] = []

    # Подписи
    responsible_person: str = ""
    initiator_name: str = ""

    # Дополнительные метрики для шаблона 3
    integration_software: List[str] = []
    refactored_tests_count: int = 0
    new_tests_count: int = 0
    regression_tests_count: int = 0

    # ========== ВЫЧИСЛЯЕМЫЕ СВОЙСТВА ==========

    @property
    def total_tests(self) -> int:
        return len(self.test_cases_table)

    @property
    def successful_tests(self) -> int:
        return sum(1 for tc in self.test_cases_table if tc.status == TestStatus.SUCCESS)

    @property
    def failed_tests(self) -> int:
        return sum(1 for tc in self.test_cases_table if tc.status == TestStatus.ERROR)

    @property
    def skipped_tests(self) -> int:
        return sum(1 for tc in self.test_cases_table if tc.status == TestStatus.SKIPPED)

    @property
    def error_percentage(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.failed_tests / self.total_tests) * 100

    @property
    def skipped_percentage(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.skipped_tests / self.total_tests) * 100

    @property
    def has_blocking_defect(self) -> bool:
        return self.blocking_defect is not None

    @property
    def run_datetime(self) -> datetime:
        return self.start_datetime

    @property
    def overall_status(self) -> str:
        if self.has_blocking_defect:
            return "блокирующий дефект"
        elif self.failed_tests > 0:
            return "с ошибкой"
        else:
            return "Успешно"

class ReportRequest(BaseModel):
    run_id: str
    template_type: str  # "summary", "short", "full"
    jwt_token: str