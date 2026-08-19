from sqlalchemy import select
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

        dto_links = list(unique_vacancies_by_link.keys())

        query = select(VacancyModel.link).where(VacancyModel.link.in_(dto_links))
        result = await self.session.execute(query)
        existing_links = set(result.scalars().all())

        new_vacancy_models = [
            VacancyModel(**dto.model_dump())
            for link, dto in unique_vacancies_by_link.items()
            if link not in existing_links
        ]

        if new_vacancy_models:
            self.session.add_all(new_vacancy_models)
            await self.session.flush()

        return len(new_vacancy_models)
