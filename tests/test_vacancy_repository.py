from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.vacancy import VacancyModel
from src.repositories.vacancy import VacancyRepository
from src.schemas import VacancyDTO


async def test_create_many_success(db_session: AsyncSession):
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

    repo = VacancyRepository(db_session)

    new_vacancies_count = await repo.create_many(vacancies)

    assert new_vacancies_count == 2

    db_vacancies_object = await db_session.execute(select(VacancyModel))
    db_vacancies = db_vacancies_object.scalars().all()

    assert len(db_vacancies) == 2

    vacancies_by_link = {vacancy.link: vacancy for vacancy in db_vacancies}

    assert "https://habr.com" in vacancies_by_link
    assert vacancies_by_link["https://habr.com"].title == "Python Developer"
    assert vacancies_by_link["https://habr.com"].company_name == "Cyber Core Tech"
    assert vacancies_by_link["https://habr.com"].salary == "от 150 000 до 250 000 ₽"

    assert "https://hh.ru" in vacancies_by_link
    assert vacancies_by_link["https://hh.ru"].title == "FastAPI Engineer"
    assert vacancies_by_link["https://hh.ru"].company_name == "Async Team"
    assert vacancies_by_link["https://hh.ru"].salary == "300 000 ₽"


async def test_create_many_deduplication(db_session: AsyncSession):
    initial_vacancy = VacancyDTO(
        title="Data Engineer",
        company_name="Big Data Corp",
        salary="з/п не указана",
        link="https://habr.com",
    )

    repo = VacancyRepository(db_session)

    await repo.create_many([initial_vacancy])

    batch_with_duplicate = [
        VacancyDTO(
            title="Data Engineer",
            company_name="Big Data Corp",
            salary="з/п не указана",
            link="https://habr.com",
        ),
        VacancyDTO(
            title="DevOps Specialist",
            company_name="Cloud Solutions",
            salary="от 200 000 ₽",
            link="https://hh.ru",
        ),
    ]

    new_vacancies_count = await repo.create_many(batch_with_duplicate)

    assert new_vacancies_count == 1

    db_vacancies_object = await db_session.execute(select(VacancyModel))
    db_vacancies = db_vacancies_object.scalars().all()

    assert len(db_vacancies) == 2

    vacancies_by_link = {vacancy.link: vacancy for vacancy in db_vacancies}

    assert "https://habr.com" in vacancies_by_link
    assert "https://hh.ru" in vacancies_by_link


async def test_create_many_internal_duplicates_in_batch(db_session: AsyncSession):
    batch_with_internal_duplicates = [
        VacancyDTO(
            title="QA Engineer",
            company_name="Testing Lab",
            salary="120 000 ₽",
            link="https://habr.com",
        ),
        VacancyDTO(
            title="DevOps Specialist",
            company_name="Cloud Solutions",
            salary="от 200 000 ₽",
            link="https://hh.ru",
        ),
        VacancyDTO(
            title="QA Engineer (Clone)",
            company_name="Testing Lab",
            salary="120 000 ₽",
            link="https://habr.com",
        ),
    ]

    repo = VacancyRepository(db_session)

    new_vacancies_count = await repo.create_many(batch_with_internal_duplicates)

    assert new_vacancies_count == 2

    db_vacancies_object = await db_session.execute(select(VacancyModel))
    db_vacancies = db_vacancies_object.scalars().all()

    assert len(db_vacancies) == 2

    vacancies_by_link = {vacancy.link: vacancy for vacancy in db_vacancies}

    assert "https://habr.com" in vacancies_by_link
    assert "https://hh.ru" in vacancies_by_link


async def test_get_all_success(db_session: AsyncSession):
    original_vacancies = [
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
    repo = VacancyRepository(db_session)

    await repo.create_many(original_vacancies)
    db_vacancies = await repo.get_all()

    assert len(db_vacancies) == 2

    vacancy = db_vacancies[0]

    assert isinstance(vacancy, VacancyDTO)

    assert vacancy.title == "Python Developer"
    assert vacancy.company_name == "Cyber Core Tech"
    assert vacancy.salary == "от 150 000 до 250 000 ₽"
    assert vacancy.link == "https://habr.com"


async def test_get_all_empty(db_session: AsyncSession):
    repo = VacancyRepository(db_session)
    vacancies = await repo.get_all()

    assert len(vacancies) == 0
