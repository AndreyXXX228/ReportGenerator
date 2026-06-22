from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import os
from dotenv import load_dotenv

from app.models import DefectStep, TestCaseDetail, TestRunData, TestStatus

load_dotenv()


class BackendClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.getenv("BACKEND_URL", "http://localhost:8080")).rstrip("/")

    async def get_test_run_data(self, run_id: str, jwt_token: str = "") -> TestRunData:
        """Получить данные для отчётов из бэкенда."""
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/api/report-data/{run_id}",
                headers=headers,
            )
            response.raise_for_status()
            return self._map_to_model(response.json())

    def _parse_datetime(self, value: Any, default: datetime | None = None) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str) and value:
            return datetime.fromisoformat(value)
        return default or datetime.now()

    def _parse_status(self, value: Any) -> TestStatus:
        if isinstance(value, TestStatus):
            return value
        try:
            return TestStatus(str(value))
        except ValueError:
            return TestStatus.SUCCESS

    def _map_defect(self, raw: Optional[Dict[str, Any]]) -> Optional[DefectStep]:
        if not raw:
            return None
        return DefectStep(
            test_case_id=str(raw.get("test_case_id", "")),
            step_number=int(raw.get("step_number", 0)),
            description=str(raw.get("description", "")),
        )

    def _map_defects(self, items: Any) -> List[DefectStep]:
        if not isinstance(items, list):
            return []
        return [defect for item in items if (defect := self._map_defect(item)) is not None]

    def _map_test_cases(self, items: Any) -> List[TestCaseDetail]:
        if not isinstance(items, list):
            return []
        test_cases = []
        for item in items:
            if not isinstance(item, dict):
                continue
            test_cases.append(
                TestCaseDetail(
                    name=str(item.get("name", "")),
                    status=self._parse_status(item.get("status", TestStatus.SUCCESS.value)),
                    duration=str(item.get("duration", "00:00:00")),
                )
            )
        return test_cases

    def _map_to_model(self, raw: Dict[str, Any]) -> TestRunData:
        blocking_defect = self._map_defect(raw.get("blocking_defect"))

        return TestRunData(
            project_name=str(raw.get("project_name", "")),
            project_description=str(raw.get("project_description", "")),
            version=str(raw.get("version", "")),
            run_name=str(raw.get("run_name", "")),
            run_version=str(raw.get("run_version", "")),
            run_description=str(raw.get("run_description", "")),
            start_datetime=self._parse_datetime(raw.get("start_datetime")),
            end_datetime=self._parse_datetime(raw.get("end_datetime")),
            test_cases_table=self._map_test_cases(raw.get("test_cases_table")),
            blocking_defect=blocking_defect,
            failed_test_cases=self._map_defects(raw.get("failed_test_cases")),
            skipped_test_cases=self._map_defects(raw.get("skipped_test_cases")),
            critical_errors=self._map_defects(raw.get("critical_errors")),
            non_critical_errors=self._map_defects(raw.get("non_critical_errors")),
            responsible_person=str(raw.get("responsible_person", "")),
            initiator_name=str(raw.get("initiator_name", "")),
            integration_software=list(raw.get("integration_software") or []),
            refactored_tests_count=int(raw.get("refactored_tests_count", 0)),
            new_tests_count=int(raw.get("new_tests_count", 0)),
            regression_tests_count=int(raw.get("regression_tests_count", 0)),
        )
