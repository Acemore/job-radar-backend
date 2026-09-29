import asyncio
import csv

import structlog
from openpyxl import Workbook

from src.schemas.vacancy import VacancyDTO

logger = structlog.get_logger()

EXPORT_HEADERS = ["Title", "Company_name", "Salary", "Link"]


async def export_vacancies_to_csv(
    vacancies: list[VacancyDTO], file_path: str = "vacancies_report.csv"
) -> None:
    if not vacancies:
        logger.warning("no_vacancies_to_export")
        return

    def _write_csv():
        with open(file_path, "w", encoding="utf-8", newline="") as file_object:
            writer = csv.writer(file_object)

            writer.writerow(EXPORT_HEADERS)

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


async def export_vacancies_to_xlsx(
    vacancies: list[VacancyDTO], file_path: str = "vacancies_report.xlsx"
) -> None:
    if not vacancies:
        logger.warning("no_vacancies_to_export")
        return

    def _write_xlsx():
        wb = Workbook()

        ws = wb.active
        ws.title = "Vacancies"

        ws.append(EXPORT_HEADERS)

        for v in vacancies:
            row = [v.title, v.company_name, v.salary, v.link]
            ws.append(row)

        wb.save(file_path)

    try:
        await asyncio.to_thread(_write_xlsx)
        logger.info("export_to_xlsx_success", path=file_path)
    except OSError as os_err:
        logger.error(
            "xlsx_export_os_error",
            path=file_path,
            error=str(os_err),
            hint="Check folder permissions or disk space",
        )
    except Exception as e:
        logger.error("xlsx_export_unexpected_error", error=str(e), exc_info=True)
