"""Tests for internal notification endpoint."""

from unittest.mock import patch

from flask.testing import FlaskClient


class TestNotifyLeaseChange:
    """Tests for POST /internal/notify-lease-change."""

    def test_notify_returns_success(self, client: FlaskClient) -> None:
        response = client.post("/internal/notify-lease-change")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

    def test_notify_reloads_cache(self, client: FlaskClient) -> None:
        """Verify that leases are still accessible after notification."""
        response = client.post("/internal/notify-lease-change")
        assert response.status_code == 200

        response = client.get("/api/dhcp/leases")
        assert response.status_code == 200
        assert len(response.get_json()) > 0

    @patch("app.services.sse_connection_manager.SSEConnectionManager.send_event")
    def test_notify_broadcasts_sse_event(self, mock_send_event, client: FlaskClient) -> None:
        response = client.post("/internal/notify-lease-change")
        assert response.status_code == 200

        mock_send_event.assert_called_once()
        call_args = mock_send_event.call_args
        assert call_args[0][0] is None  # Broadcast (no specific request_id)
        assert call_args[0][2] == "data_changed"
        assert call_args[0][3] == "dhcp"
