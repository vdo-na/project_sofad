from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Тест 1: Проверка эндпоинта /health (Smoke-тест)"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_metrics_endpoint():
    """Тест 2: Проверка, что Prometheus-метрики отдаются сервером"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "process_cpu_seconds_total" in response.text

def test_create_city_validation():
    """Тест 3: Проверка валидации входных данных (защита от некорректных координат)"""
    # Передаем невалидную широту (150 при максимуме 90)
    invalid_data = {
        "city_name": "InvalidCity",
        "latitude": 150.0,
        "longitude": 30.0
    }
    response = client.post("/api/v1/cities", json=invalid_data)
    # Сервер должен отловить ошибку валидации и вернуть 422 Unprocessable Entity
    assert response.status_code == 422