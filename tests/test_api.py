def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status": "OK"}


def test_get_vacancies_endpoint(client, seed_vacancies):
    response = client.get("/api/vacancies")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0] == {"title": "Python Developer", "company_name": "Google"}
