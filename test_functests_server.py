# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import server
import socket
import pytest
import time
from multiprocessing import Process


addr = ("127.0.0.1", 8000)


@pytest.yield_fixture(scope='session', autouse=True)
def server_setup():
    process = Process(target=server.run_server)
    process.daemon = True
    process.start()
    time.sleep(0.1)
    yield process


@pytest.fixture(scope='function')
def client_setup():
    client = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
    )
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.connect(addr)
    return client


################
# FUNCTIONAL TESTS
################


def test_client_ok_response(client_setup):
    client = client_setup
    client.sendall(b"GET / HTTP/1.1\r\nHost: www.host.com:80\r\n\r\n")
    expected_response = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<html><img src="webroot/images/sample_1.png"></html>'
    )
    server_response = client.recv(4096)
    client.close()
    assert expected_response in server_response

# Ensure that the body of the requested resource is returned in a "200 OK"
# response.

# The response should include the appropriate header to indicate the type of
# resource being returned.

# The response should also include the appropriate header to indicate the
# amount of content being returned.

# The response should include any other valid HTTP headers you wish to add.


def test_response_ok(client_setup):
    client = client_setup
    client.sendall(
        b"GET webroot/images/sample_1.png HTTP/1.1\r\n"
        b"Host: www.host.com:80\r\n"
        b"\r\n"
    )
    expected_response = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<html><img src="webroot/images/sample_1.png"></html>'
    )
    server_response = client.recv(4096)
    client.close()
    assert expected_response == server_response
