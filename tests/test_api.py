def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status": "OK"}


def test_get_vacancies_endpoint(client, seed_vacancies):
    response = client.get("/api/vacancies")

    assert response.status_code == 200

    db_vacancies = response.json()

    assert len(db_vacancies) == 2

    vacancies_by_link = {vacancy["link"]: vacancy for vacancy in db_vacancies}

    assert vacancies_by_link["https://habr.com"]["title"] == "Python Developer"
    assert vacancies_by_link["https://habr.com"]["company_name"] == "Google"
    assert vacancies_by_link["https://habr.com"]["salary"] == "150000"

    assert vacancies_by_link["https://hh.ru"]["title"] == "FastAPI Engineer"
    assert vacancies_by_link["https://hh.ru"]["company_name"] == "Yandex"
    assert vacancies_by_link["https://hh.ru"]["salary"] == "200000"
