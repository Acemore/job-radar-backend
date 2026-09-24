from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.vacancy import VacancyModel
from src.schemas import VacancyDTO


class VacancyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(self, vacancies: list[VacancyDTO]) -> int:
        if not vacancies:
            return 0

        unique_vacancies_by_link = {vacancy.link: vacancy for vacancy in vacancies}

        values = [dto.model_dump() for dto in unique_vacancies_by_link.values()]

        stmt = pg_insert(VacancyModel).values(values)
        stmt = stmt.on_conflict_do_nothing(index_elements=[VacancyModel.link])

        result = await self.session.execute(stmt)
        await self.session.flush()

        return result.rowcount

    async def get_all(self) -> list[VacancyDTO]:
        result = await self.session.execute(select(VacancyModel))
        db_vacancies = result.scalars().all()

        dto_vacancies = [
            VacancyDTO.model_validate(db_vacancy) for db_vacancy in db_vacancies
        ]

        return dto_vacancies
