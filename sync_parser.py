import time

PAGES_COUNT = 10


def fetch_page(page_num: int):
    print(f"[Синхронно] Начал скачивать страницу {page_num}")
    # Чистое ожидание в 1 секунду без сетевых запросов
    time.sleep(1)
    print(f"[Синхронно] Закончил скачивать страницу {page_num} -> Статус: 200")


def main():
    start_time = time.time()

    print("=== СТАРТ СИНХРОННОГО ПАРСЕРА ===")

    for page in range(1, PAGES_COUNT + 1):
        fetch_page(page)

    end_time = time.time()
    print(f"=== ВСЕГО ЗАТРАЧЕНО ВРЕМЕНИ: {end_time - start_time:.2f} сек ===")


if __name__ == "__main__":
    main()
