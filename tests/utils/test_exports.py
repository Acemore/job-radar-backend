import pytest

from src.schemas.vacancy import VacancyDTO
from src.utils.exports import export_vacancies_to_csv


@pytest.mark.asyncio
async def test_export_vacancies_to_csv_success(tmp_path):
    vacancies = [
        VacancyDTO(
            title="Python Developer",
            company_name="Cyber Core Tech",
            salary="от 150 000 до 250 000 ₽",
            link="https://habr.com",
        ),
        VacancyDTO(
            title="FastAPI Engineer",
            company_name="Async Team",
            salary="300 000 ₽",
            link="https://hh.ru",
        ),
    ]

    test_file = tmp_path / "test_report.csv"

    await export_vacancies_to_csv(vacancies, file_path=str(test_file))

    assert test_file.exists()

    rows = test_file.read_text(encoding="utf-8").splitlines()

    assert rows[0] == "Title,Company_name,Salary,Link"
    assert (
        rows[1]
        == "Python Developer,Cyber Core Tech,от 150 000 до 250 000 ₽,https://habr.com"
    )
