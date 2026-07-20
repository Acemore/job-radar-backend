import asyncio
import asyncpg


async def main():
    dsn = "postgres://postgres:postgres@127.0.0.1:5432/job_radar"

    print("[БД] Попытка асинхронного подключения...")

    conn = await asyncpg.connect(dsn)

    print("[БД] Подключение успешно! Выполняю тестовый запрос...")

    result = await conn.fetchval('SELECT 1;')

    print(f"[БД] Ответ от базы получен: {result}")

    await conn.close()

    print("[БД] Соединение закрыто.")

if __name__ == "__main__":
    asyncio.run(main())
