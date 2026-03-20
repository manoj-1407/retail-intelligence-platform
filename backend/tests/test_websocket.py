from __future__ import annotations
import json
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture(scope="module")
def ws_client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


class TestWebSocketAuth:
    def test_missing_token_rejected(self, ws_client):
        closed = False
        try:
            with ws_client.websocket_connect("/ws/inventory") as ws:
                ws.receive_text()
        except Exception:
            closed = True
        assert closed, "Expected connection to be refused without token"

    def test_invalid_token_rejected(self, ws_client):
        closed = False
        try:
            with ws_client.websocket_connect(
                    "/ws/inventory?token=bad.token.here") as ws:
                ws.receive_text()
        except Exception:
            closed = True
        assert closed, "Expected connection to be refused with invalid token"


class TestWebSocketData:
    def test_valid_token_accepted_and_receives_message(self, ws_client, admin_token):
        received = None
        try:
            with ws_client.websocket_connect(
                    f"/ws/inventory?token={admin_token}") as ws:
                raw = ws.receive_text()
                received = json.loads(raw)
        except Exception as e:
            pytest.fail(f"WebSocket connection failed unexpectedly: {e}")

        assert received is not None
        assert "type" in received
        assert received["type"] == "low_stock"
        assert "data" in received
        assert isinstance(received["data"], list)

    def test_viewer_token_accepted(self, ws_client, viewer_token):
        try:
            with ws_client.websocket_connect(
                    f"/ws/inventory?token={viewer_token}") as ws:
                raw = ws.receive_text()
                msg = json.loads(raw)
                assert msg["type"] == "low_stock"
        except Exception as e:
            pytest.fail(f"Viewer WebSocket connection failed: {e}")
