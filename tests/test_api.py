# pyrefly: ignore [missing-import]
from unittest.mock import patch

import pytest

import app as app_module

VALID_PAYLOAD = {
    "cpu": {"percent": 10.0},
    "memory": {"percent": 20.0},
    "disk": {"percent": 30.0},
}


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module._history_lock:
        app_module.metrics_history.clear()
    with app_module.app.test_client() as test_client:
        yield test_client


def post_metrics(client, payload, key=None):
    headers = {"X-API-Key": app_module.API_KEY if key is None else key}
    return client.post("/api/metrics", json=payload, headers=headers)


def test_health(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


@pytest.mark.parametrize("key", ["", "wrong-key"])
def test_post_rejects_invalid_api_key(client, key):
    response = post_metrics(client, VALID_PAYLOAD, key=key)

    assert response.status_code == 403
    assert client.get("/api/metrics/history").get_json() == []


def test_post_rejects_missing_api_key(client):
    response = client.post("/api/metrics", json=VALID_PAYLOAD)

    assert response.status_code == 403


def test_post_rejects_non_json_body(client):
    response = client.post(
        "/api/metrics", data="not json", headers={"X-API-Key": app_module.API_KEY}
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {"memory": {"percent": 1}, "disk": {"percent": 1}},
        {**VALID_PAYLOAD, "cpu": {"percent": "high"}},
        {**VALID_PAYLOAD, "cpu": {"percent": True}},
        {**VALID_PAYLOAD, "cpu": {"percent": 150}},
        {**VALID_PAYLOAD, "disk": []},
    ],
)
def test_post_rejects_malformed_payload(client, payload):
    response = post_metrics(client, payload)

    assert response.status_code == 400
    assert "details" in response.get_json()


def test_post_records_normalized_snapshot(client):
    response = post_metrics(client, VALID_PAYLOAD)

    assert response.status_code == 201
    history = client.get("/api/metrics/history").get_json()
    assert len(history) == 1
    snapshot = history[0]
    assert snapshot["status"] == "healthy"
    assert snapshot["alerts"] == []
    assert snapshot["network"] == {"download_mb": 0.0, "upload_mb": 0.0}
    assert snapshot["timestamp"].endswith("Z")


def test_post_flags_threshold_breaches(client):
    payload = {**VALID_PAYLOAD, "cpu": {"percent": 99.0}}

    post_metrics(client, payload)

    snapshot = client.get("/api/metrics/history").get_json()[0]
    assert snapshot["status"] == "warning"
    assert any("CPU" in alert for alert in snapshot["alerts"])


def test_history_is_bounded(client):
    limit = app_module.metrics_history.maxlen
    for i in range(limit + 5):
        post_metrics(client, {**VALID_PAYLOAD, "timestamp": f"t{i}"})

    history = client.get("/api/metrics/history").get_json()
    assert len(history) == limit
    assert history[0]["timestamp"] == "t5"
    assert history[-1]["timestamp"] == f"t{limit + 4}"


def test_get_metrics_collects_local_snapshot(client):
    with (
        patch.object(app_module, "get_cpu_usage", return_value={"percent": 95.0, "error": None}),
        patch.object(app_module, "get_memory_usage", return_value={"percent": 40.0, "error": None}),
        patch.object(app_module, "get_disk_usage", return_value={"percent": 50.0, "error": None}),
        patch.object(
            app_module,
            "get_network_usage",
            return_value={"download_mb": 1.0, "upload_mb": 0.5, "error": None},
        ),
        patch.object(app_module, "get_top_processes", return_value=[]),
    ):
        response = client.get("/api/metrics")

    body = response.get_json()
    assert response.status_code == 200
    assert body["status"] == "warning"
    assert body["network"]["download_mb"] == 1.0
    assert len(client.get("/api/metrics/history").get_json()) == 1


def test_get_metrics_reports_sensor_errors_as_alerts(client):
    with (
        patch.object(app_module, "get_cpu_usage", return_value={"percent": 0.0, "error": "boom"}),
        patch.object(app_module, "get_memory_usage", return_value={"percent": 0.0, "error": None}),
        patch.object(app_module, "get_disk_usage", return_value={"percent": 0.0, "error": None}),
        patch.object(app_module, "get_network_usage", return_value={"error": None}),
        patch.object(app_module, "get_top_processes", return_value=[]),
    ):
        body = client.get("/api/metrics").get_json()

    assert "CPU sensor error: boom" in body["alerts"]


def test_unknown_api_route_returns_json_404(client):
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.is_json
