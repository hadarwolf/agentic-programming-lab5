"""The HTTP server, run on a free port in a background thread."""

import json
import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from typing import Any

import pytest

from server import make_server


@pytest.fixture
def base_url() -> Iterator[str]:
    server = make_server(0)
    thread = threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()


def post(base_url: str, body: bytes) -> tuple[int, Any]:
    request = urllib.request.Request(f"{base_url}/api/action", data=body, method="POST")
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


def test_state_and_a_move(base_url: str) -> None:
    with urllib.request.urlopen(f"{base_url}/api/state") as response:
        assert json.load(response)["turn"] == "w"
    action = {"action": "move", "source": "e2", "target": "e4"}
    status, view = post(base_url, json.dumps(action).encode())
    assert status == 200
    assert view["moves"] == ["e2-e4"]
    assert view["turn"] == "b"


def test_static_files_are_served(base_url: str) -> None:
    with urllib.request.urlopen(f"{base_url}/") as response:
        assert response.headers["Content-Type"].startswith("text/html")
        assert b"Redo" in response.read()


@pytest.mark.parametrize(
    "body",
    [b"[1, 2]", b"not json", json.dumps({"action": "fly"}).encode()],
)
def test_bad_actions_are_rejected(base_url: str, body: bytes) -> None:
    status, reply = post(base_url, body)
    assert status == 400
    assert "error" in reply


def test_unknown_paths_are_not_found(base_url: str) -> None:
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(f"{base_url}/secret.txt")
    assert error.value.code == 404
    request = urllib.request.Request(f"{base_url}/api/nope", data=b"{}", method="POST")
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(request)
    assert error.value.code == 404
