from datetime import datetime
from typing import Any, Dict, List, Optional
from app.models import DefectStep, TestCaseDetail, TestStatus, RawStatus


def ms_to_time_str(ms: int) -> str:
    if not ms:
        return "00:00:00"
    seconds = ms // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def parse_datetime(value: Any, default: Optional[datetime] = None) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    return default or datetime.now()

def parse_status(value: Any) -> TestStatus:
    if isinstance(value, TestStatus):
        return value
    try:
        if value in [TestStatus.SUCCESS.value, TestStatus.ERROR.value, TestStatus.SKIPPED.value]:
            return TestStatus(value)
        raw = RawStatus(str(value))
        if raw == RawStatus.SUCCESS or raw == RawStatus.NOT_STARTED:
            return TestStatus.SUCCESS
        elif raw == RawStatus.ERROR:
            return TestStatus.ERROR
        elif raw == RawStatus.SKIPPED:
            return TestStatus.SKIPPED
        else:
            return TestStatus.SUCCESS
    except (ValueError, TypeError):
        return TestStatus.SUCCESS

def map_defect(self, raw: Optional[Dict[str, Any]]) -> Optional[DefectStep]:
    if not raw:
        return None
    return DefectStep(
        test_case_id=str(raw.get("test_case_id", "")),
        step_number=int(raw.get("step_number", 0)),
        description=str(raw.get("description", "")),
    )

def map_defects(items: Any) -> List[DefectStep]:
    if not isinstance(items, list):
        return []
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        defect = map_defect(item)
        if defect:
            result.append(defect)
    return result


def map_test_cases(items: Any) -> List[TestCaseDetail]:
    if not isinstance(items, list):
        return []
    test_cases = []
    for item in items:
        if not isinstance(item, dict):
            continue

        duration_raw = item.get("duration", 0)
        if isinstance(duration_raw, (int, float)):
            duration_str = ms_to_time_str(int(duration_raw))
        else:
            duration_str = str(duration_raw)

        test_cases.append(
            TestCaseDetail(
                name=str(item.get("name", "")),
                status=parse_status(item.get("status", "NOT_STARTED")),
                duration=duration_str,
            )
        )
    return test_cases