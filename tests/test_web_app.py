from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health_endpoint_is_healthy():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_status_does_not_expose_api_key():
    response = client.get("/api/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Nova-AJ"
    assert "OPENAI_API_KEY" not in str(payload)


def test_web_app_shell_is_served():
    response = client.get("/app/")
    assert response.status_code == 200
    assert "Nova AJ" in response.text
    assert 'id="chat-form"' in response.text


def test_pwa_manifest_is_served():
    response = client.get("/app/manifest.webmanifest")
    assert response.status_code == 200
    assert response.json()["start_url"] == "/app/"
    assert response.json()["display"] == "standalone"


def test_service_worker_is_served():
    response = client.get("/app/service-worker.js")
    assert response.status_code == 200
    assert "addEventListener" in response.text


def test_chat_rejects_empty_message():
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422
