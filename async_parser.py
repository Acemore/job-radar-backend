import asyncio
import time

PAGES_COUNT = 10


# Ключевое слово async превращает обычную функцию в корутину (coroutine)
async def fetch_page_async(page_num: int):
    print(f"[Асинхронно] Начал скачивать страницу {page_num}")

    # Вместо блокирующего time.sleep мы используем асинхронный asyncio.sleep.
    # Ключевое слово await говорит программе: «Пока тикает эта секунда,
    # текущая функция засыпает, и мы отдаем управление обратно в Event Loop».
    await asyncio.sleep(1)

    print(f"[Асинхронно] Закончил скачивать страницу {page_num} -> Статус: 200")


async def main():
    start_time = time.time()
    print("=== СТАРТ АСИНХРОННОГО ПАРСЕРА ===")

    # Создаем пустой список для наших будущих задач (Tasks)
    tasks = []

    for page in range(1, PAGES_COUNT + 1):
        # asyncio.create_task упаковывает корутину в задачу и
        # моментально регистрирует её в Event Loop на выполнение.
        task = asyncio.create_task(fetch_page_async(page))
        tasks.append(task)

    # asyncio.gather принимает список задач и запускает их ОДНОВРЕМЕННО (конкурентно).
    # Звёздочка распаковывает список задач в аргументы функции.
    await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"=== ВСЕГО ЗАТРАЧЕНО ВРЕМЕНИ: {end_time - start_time:.2f} сек ===")

if __name__ == "__main__":
    # Эта строка создает Event Loop (цикл событий), запускает его
    # и передает ему главную асинхронную функцию как точку входа.
    asyncio.run(main())
