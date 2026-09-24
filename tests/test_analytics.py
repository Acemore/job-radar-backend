from src.parsers.constants import DEFAULT_SALARY
from src.utils.analytics import calculate_salary_breakdown, parse_salary_to_numeric


def test_parse_salary_to_numeric_salary_range():
    assert parse_salary_to_numeric("150000-220000 RUR") == 185000


def test_parse_salary_to_numeric_min_salary():
    assert parse_salary_to_numeric("от 150000 руб.") == 150000


def test_parse_salary_to_numeric_max_salary():
    assert parse_salary_to_numeric("до 100000 rur") == 100000


def test_parse_salary_to_numeric_fix_salary():
    assert parse_salary_to_numeric("100000 rur") == 100000


def test_parse_salary_to_numeric_no_salary():
    assert parse_salary_to_numeric("") is None
    assert parse_salary_to_numeric(DEFAULT_SALARY) is None
    assert parse_salary_to_numeric("по результатам собеседования") is None


def test_calculate_salary_breakdown():
    assert calculate_salary_breakdown([100000, 150000, 200000]) == {
        "min_salary": 100000,
        "max_salary": 200000,
        "avg_salary": 150000,
    }
    assert calculate_salary_breakdown([]) is None
