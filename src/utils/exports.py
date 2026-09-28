import asyncio
import csv

import structlog

from src.schemas.vacancy import VacancyDTO

logger = structlog.get_logger()


async def export_vacancies_to_csv(
    vacancies: list[VacancyDTO], file_path: str = "vacancies_report.csv"
) -> None:
    if not vacancies:
        logger.warning("no_vacancies_to_export")
        return

    headers = ["Title", "Company_name", "Salary", "Link"]

    def _write_csv():
        with open(file_path, "w", encoding="utf-8", newline="") as file_object:
            writer = csv.writer(file_object)

            writer.writerow(headers)

            for v in vacancies:
                row = [v.title, v.company_name, v.salary, v.link]
                writer.writerow(row)

    try:
        await asyncio.to_thread(_write_csv)
        logger.info("export_to_csv_success", path=file_path)
    except OSError as os_err:
        logger.error(
            "csv_export_os_error",
            path=file_path,
            error=str(os_err),
            hint="Check folder permissions or disk space",
        )
    except Exception as e:
        logger.error("csv_export_unexpected_error", error=str(e), exc_info=True)
