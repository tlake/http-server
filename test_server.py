import server
import socket
import pytest
from multiprocessing import Process


@pytest.yield_fixture()
def server_setup():
    process = Process(target=server.run_server)
    process.daemon = True
    process.start()
    yield process


@pytest.fixture()
def client_setup():
    client = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
    )
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.connect(server.addr)
    return client


def test_response_ok(server_setup):
    response_body = '<html><body><h1></h1>'\
        '<p>All good here, captain.</p></body></html>'
    assert response_body in server.response_ok()


def test_response_ok_fail():
    response_body = '<html><body><h1></h1>'\
        '<p>Your server no bueno.</p></body></html>'
    assert response_body in server.response_error()


def test_client_ok_response(client_setup):
    ok_resp = server.response_ok()
    client_setup.sendall(ok_resp)
    server_response = client_setup.recv(4096)
    expected_response = 'All good here, captain.'
    assert expected_response in server_response
