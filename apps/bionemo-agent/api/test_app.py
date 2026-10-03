from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_rejects_invalid_sequence():
    response = client.post('/api/v1/structure', json={'sequence': 'ACD123'})
    assert response.status_code == 422


def test_requires_api_key(monkeypatch):
    monkeypatch.delenv('NGC_API_KEY', raising=False)
    response = client.post('/api/v1/structure', json={'sequence': 'MKT'})
    assert response.status_code == 503
