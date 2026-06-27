from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import os
from dotenv import load_dotenv
from py_eureka_client import eureka_client

from app.models import DefectStep, TestCaseDetail, TestRunData, TestStatus

from app.utils import (
    parse_datetime,
    map_defect,
    map_defects,
    map_test_cases,
)

load_dotenv()


class BackendClient:
    def __init__(
            self,
            base_url: str | None = None,
            service_name: str | None = None,
            use_eureka: bool | None = None,
    ):
        self.base_url = (base_url or os.getenv("BACKEND_URL", "")).rstrip("/")
        self.service_name = service_name or os.getenv("BACKEND_SERVICE_NAME", "project-service")

        if use_eureka is not None:
            self.use_eureka = use_eureka
        else:
            self.use_eureka = os.getenv("USE_EUREKA", "true").lower() == "true"
        self._cached_url: str | None = None

    async def get_test_run_data(self, run_id: str) -> TestRunData:
        url = await self._get_backend_url(run_id)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return self._map_to_model(response.json())

    async def _get_backend_url(self, run_id: str) -> str:
        if self.use_eureka and self.service_name:
            try:
                if self._cached_url is None:
                    service_url = await eureka_client.get_service_url(self.service_name)
                    if service_url:
                        self._cached_url = service_url.rstrip("/")
                        print(f"Получен URL через Eureka: {self._cached_url}")
                    else:
                        print(f"Сервис '{self.service_name}' не найден в Eureka")

                if self._cached_url:
                    return f"{self._cached_url}/api/report-data/{run_id}"

            except Exception as e:
                print(f"Ошибка при получении URL через Eureka: {e}")

        # Fallback: используем статический URL
        if self.base_url:
            return f"{self.base_url}/api/report-data/{run_id}"

        raise RuntimeError(
            "Не удалось определить URL для бэкенда. "
            "Проверьте настройки BACKEND_URL или USE_EUREKA."
        )

    def _map_to_model(self, raw: Dict[str, Any]) -> TestRunData:
        blocking_defect = map_defect(raw.get("blocking_defect"))

        return TestRunData(
            project_name=str(raw.get("project_name", "")),
            project_description=str(raw.get("project_description", "")),
            version=str(raw.get("version", "")),
            run_name=str(raw.get("run_name", "")),
            run_version=str(raw.get("run_version", "")),
            run_description=str(raw.get("run_description", "")),
            start_datetime=parse_datetime(raw.get("start_datetime")),
            end_datetime=parse_datetime(raw.get("end_datetime")),
            test_cases_table=map_test_cases(raw.get("test_cases_table")),
            blocking_defect=blocking_defect,
            failed_test_cases=map_defects(raw.get("failed_test_cases")),
            skipped_test_cases=map_defects(raw.get("skipped_test_cases")),
            critical_errors=map_defects(raw.get("critical_errors")),
            non_critical_errors=map_defects(raw.get("non_critical_errors")),
            responsible_person=str(raw.get("responsible_person", "")),
            initiator_name=str(raw.get("initiator_name", "")),
            integration_software=list(raw.get("integration_software") or []),
            refactored_tests_count=int(raw.get("refactored_tests_count", 0)),
            new_tests_count=int(raw.get("new_tests_count", 0)),
            regression_tests_count=int(raw.get("regression_tests_count", 0)),
        )
