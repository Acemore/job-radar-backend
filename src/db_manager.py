import asyncpg


async def save_vacancies(pool: asyncpg.Pool, vacancies: list[dict]):
    async with pool.acquire() as conn:
        query = "INSERT INTO vacancies (title, company_name) VALUES ($1, $2);"

        for vacancy in vacancies:
            title = vacancy["title"]
            company_name = vacancy["company_name"]

            await conn.execute(query, title, company_name)
