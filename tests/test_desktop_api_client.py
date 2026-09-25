"""Transport regression tests: no real network or user database required."""
from unittest.mock import Mock, patch

import pytest

from desktop.api_client import ApiClient


@pytest.mark.parametrize("character_id,method", [(None, "post"), (7, "put")])
def test_save_pf1e_reaches_transport(character_id, method):
    client = ApiClient()
    client.set_token("test-token")
    character = {"system": "PF1E", "name": "Valeros"}
    response = Mock()
    response.json.return_value = {"id": 7}
    with patch(f"desktop.api_client.requests.{method}", return_value=response) as request:
        assert client.save_character(character, character_id, revision=1) == {"id": 7}
    assert request.call_args.kwargs["json"]["system"] == "pf1e"
    assert request.call_args.kwargs["headers"]["Authorization"] == "Bearer test-token"
    response.raise_for_status.assert_called_once()


def test_sync_rejects_mixed_system_batch_before_sending():
    with patch("desktop.api_client.requests.post") as request:
        with pytest.raises(ValueError):
            ApiClient().sync_characters([{"system": "pf1e"}, {"system": "dnd5e"}])
        request.assert_not_called()


@pytest.mark.parametrize("records", [[], [{"system": "PATHFINDER1E"}]])
def test_sync_accepts_pf1e_and_pull_only_requests(records):
    response = Mock()
    response.json.return_value = {"status": "ok"}
    with patch("desktop.api_client.requests.post", return_value=response) as request:
        assert ApiClient().sync_characters(records, "cursor") == {"status": "ok"}
    assert request.call_args.kwargs["json"] == {
        "last_sync_timestamp": "cursor", "dirty_characters": records,
    }


def test_v2_transport_preserves_operation_and_token():
    client = ApiClient()
    client.set_token('fixed-token', 'alice')
    operations = [{'system': 'pf1e', 'operation_id': 'retry-me', 'base_revision': 7}]
    response = Mock()
    response.json.return_value = {'protocol_version': 2}
    with patch('desktop.api_client.requests.post', return_value=response) as request:
        assert client.sync_v2(operations) == {'protocol_version': 2}
    assert request.call_args.args[0].endswith('/api/sync/v2')
    assert request.call_args.kwargs['json'] == {'operations': operations}
    assert request.call_args.kwargs['headers']['Authorization'] == 'Bearer fixed-token'
    response.raise_for_status.assert_called_once()
