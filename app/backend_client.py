from app.models import TestRunData, TestCaseDetail, DefectStep, TestStatus
from datetime import datetime


class BackendClient:
    def __init__(self, base_url: str = "http://backend:8000"):
        self.base_url = base_url

    async def get_test_run_data(self, run_id: str) -> TestRunData:
        _ = run_id

        return TestRunData(
            project_name="Авторизация и профиль",
            version="3.0.1",
            run_name="Регрессионное тестирование основной функциональности",
            run_version="3.0.1-RC2",
            total_tests=50,
            successful_tests=42,
            failed_tests=5,
            skipped_tests=3,
            error_percentage=10.0,
            skipped_percentage=6.0,
            has_blocking_defect=False,
            blocking_defect=None,
            failed_test_cases=[
                DefectStep(test_case_id="TC-101", step_number=3, description="Ошибка валидации формы регистрации"),
                DefectStep(test_case_id="TC-102", step_number=1, description="Не загружается страница профиля"),
                DefectStep(test_case_id="TC-105", step_number=4, description="Неверный расчёт суммы в корзине"),
                DefectStep(test_case_id="TC-108", step_number=2, description="Ошибка при отправке формы"),
                DefectStep(test_case_id="TC-110", step_number=3, description="Таймаут при загрузке данных"),
            ],
            skipped_test_cases=[
                DefectStep(test_case_id="TC-201", step_number=2, description="Зависит от TC-101"),
                DefectStep(test_case_id="TC-202", step_number=1, description="Зависит от TC-102"),
                DefectStep(test_case_id="TC-203", step_number=2, description="Зависит от TC-105"),
            ],
            critical_errors=[
                DefectStep(test_case_id="TC-101", step_number=3, description="Ошибка валидации формы регистрации"),
                DefectStep(test_case_id="TC-102", step_number=1, description="Не загружается страница профиля"),
            ],
            non_critical_errors=[
                DefectStep(test_case_id="TC-105", step_number=4, description="Неверный расчёт суммы в корзине"),
                DefectStep(test_case_id="TC-108", step_number=2, description="Ошибка при отправке формы"),
                DefectStep(test_case_id="TC-110", step_number=3, description="Таймаут при загрузке данных"),
            ],
            test_cases_table=[
                TestCaseDetail(name="Авторизация", status=TestStatus.SUCCESS, duration="00:00:05"),
                TestCaseDetail(name="Регистрация", status=TestStatus.ERROR, duration="00:00:08"),
                TestCaseDetail(name="Поиск", status=TestStatus.SUCCESS, duration="00:00:03"),
                TestCaseDetail(name="Фильтрация", status=TestStatus.SUCCESS, duration="00:00:04"),
                TestCaseDetail(name="Экспорт", status=TestStatus.SKIPPED, duration="00:00:00"),
                TestCaseDetail(name="Импорт", status=TestStatus.SUCCESS, duration="00:00:06"),
                TestCaseDetail(name="Удаление", status=TestStatus.SUCCESS, duration="00:00:02"),
                TestCaseDetail(name="Редактирование", status=TestStatus.SUCCESS, duration="00:00:07"),
                TestCaseDetail(name="Копирование", status=TestStatus.SUCCESS, duration="00:00:03"),
                TestCaseDetail(name="Перемещение", status=TestStatus.SUCCESS, duration="00:00:04"),
            ],
            responsible_person="Иванов И.И.",
            initiator_name="Петров П.П.",
            run_datetime=datetime.now()
        )