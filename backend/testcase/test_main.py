from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# the main service test case
def test_main():
    response= client.get('/')
    assert response.status_code == 200

# the api test case
def test_api():
    response= client.get('/api/v1')
    assert response.status_code == 200
