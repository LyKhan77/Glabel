from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_hardware_info():
    response = client.get("/api/v1/system/hardware")
    assert response.status_code == 200
    data = response.json()
    assert "os" in data
    assert "cpu" in data
    assert "ram_gb" in data
    assert "recommended_models" in data
    assert isinstance(data["recommended_models"], list)
