import re

import structlog

from src.parsers.constants import DEFAULT_SALARY

logger = structlog.get_logger()


def parse_salary_to_numeric(salary_text: str) -> int | None:
    try:
        normalized_salary_text = salary_text.strip().lower()

        if not normalized_salary_text or normalized_salary_text == DEFAULT_SALARY:
            return None

        sanitized_salary_text = re.sub(r"[^0-9-]", "", normalized_salary_text)

        if not sanitized_salary_text:
            return None

        if "-" in sanitized_salary_text:
            s_from, s_to = [*map(int, sanitized_salary_text.split("-"))]

            return (s_from + s_to) // 2

        if sanitized_salary_text.isdigit():
            return int(sanitized_salary_text)

        return None
    except ValueError as e:
        logger.warning(
            "failed_to_parse_salary_string", salary=salary_text, error=str(e)
        )
        return None


def calculate_salary_breakdown(salaries: list[int]) -> dict[str, int] | None:
    if not salaries:
        return None

    min_salary = min(salaries)
    max_salary = max(salaries)
    avg_salary = sum(salaries) // len(salaries)

    return {
        "min_salary": min_salary,
        "max_salary": max_salary,
        "avg_salary": avg_salary,
    }
