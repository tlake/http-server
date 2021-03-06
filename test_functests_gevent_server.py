# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import gevent_server
import socket
import pytest
import time
from multiprocessing import Process


addr = ("127.0.0.1", 8000)
_CRLF = b'\r\n'


# yield fixtures are demons

# We used to have a yield fixture here and in the server.py tests
# which would start up the server and keep it going, I thought, until
# the end of its scope. Since these server fixtures were scoped to
# module, we believed they would terminate at the end of the module.
# The theory seemed to hold true through the end of Step 3, since we
# only ever started one server throughout the entire testing process.
# Once we created the gevent server, there were within the test suite
# two different server creation fixtures, both scoped to module. We
# falsely believed that each of these fixtures would terminate at the
# end of the module. In practice, it seems that a yield fixture doesn't
# terminate until the end of the entire testing session, regardless
# of defined scope.

# The solution, seen below, is to use just a regular fixture with
# a process-terminating finalizer. The scope behaves properly,
# and autouse also still works.


@pytest.fixture(scope='module', autouse=True)
def gevent_server_setup(request):
    process = Process(target=gevent_server.run_gevent_server)
    process.daemon = True
    process.start()
    time.sleep(0.1)

    def cleanup():
        process.terminate()

    request.addfinalizer(cleanup)
    return process


@pytest.fixture(scope='function')
def client_setup():
    client = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
    )
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.connect(addr)
    return client


def verify_response(response):
    assert 2 * _CRLF in response
    head_and_body = response.split((2 * _CRLF), 1)
    head_chunk = head_and_body[0].split(_CRLF)
    first_line = head_chunk[0].split()
    assert first_line[0] == b"HTTP/1.1"
    assert first_line[1].isdigit()
    assert first_line[2] is not None


################
# FUNCTIONAL TESTS
################


def test_client_receives_ok_on_image_request(client_setup):
    client = client_setup
    request = _CRLF.join([
        b"GET /images/sample_1.png HTTP/1.1",
        b"Host: www.host.com:80",
        b""
    ])
    ok_header = b"HTTP/1.1 200 OK"
    content_type = b'image'
    client.sendall(request)
    server_response = client.recv(4096)
    client.close()
    verify_response(server_response)
    assert ok_header in server_response
    assert content_type in server_response


def test_client_receives_ok_on_textfile_request(client_setup):
    client = client_setup
    request = _CRLF.join([
        b"GET /sample.txt HTTP/1.1",
        b"Host: www.host.com:80",
        b""
    ])
    ok_header = b"HTTP/1.1 200 OK"
    content_type = b'text/plain'
    client.sendall(request)
    server_response = client.recv(4096)
    client.close()
    verify_response(server_response)
    assert ok_header in server_response
    assert content_type in server_response


def test_client_receives_sample_txt_on_request(client_setup):
    client = client_setup
    client.sendall(
        b"GET /sample.txt HTTP/1.1\r\n"
        b"Host: www.host.com:80\r\n"
        b"\r\n"
    )
    text = (
        "This is a very simple text file.\n"
        "Just to show that we can server it up.\n"
        "It is three lines long."
    )
    server_response = client.recv(4096)
    client.close()
    verify_response(server_response)
    assert text in server_response


def test_client_receives_root_filesystem(client_setup):
    client = client_setup
    client.sendall(b"GET / HTTP/1.1\r\nHost: www.host.com:80\r\n\r\n")
    expected_response = [
        '<li>a_web_page.html</li>',
        '<li>sample.txt</li>',
        '<li>make_time.py</li>',
        '<li>images</li>'
    ]
    server_response = client.recv(4096)
    client.close()
    verify_response(server_response)
    for line in expected_response:
        assert line in server_response


def test_client_receives_error_on_not_get(client_setup):
    client = client_setup
    client.sendall(b"POST / HTTP/1.1\r\nHost: www.host.com:80\r\n\r\n")
    expected_response = (b"405 Method Not Allowed")
    server_response = client.recv(4096)
    client.close()
    verify_response(server_response)
    assert expected_response in server_response


def test_client_receives_error_on_bad_request(client_setup):
    client = client_setup
    client.sendall(b"GET / HTTP/1.9\r\nHost: www.host.com:80\r\n\r\n")
    expected_response = (b"400 Bad Request")
    server_response = client.recv(4096)
    client.close()
    verify_response(server_response)
    assert expected_response in server_response


def test_client_receives_error_on_no_host(client_setup):
    client = client_setup
    client.sendall(b"GET / HTTP/1.1\r\n\r\n")
    expected_response = (b"406 Not Acceptable")
    server_response = client.recv(4096)
    client.close()
    verify_response(server_response)
    assert expected_response in server_response


def test_client_receives_error_on_bad_uri(client_setup):
    client = client_setup
    client.sendall(b"GET /sadsge HTTP/1.1\r\nHost: www.host.com:80\r\n\r\n")
    expected_response = (b"404 Not Found")
    server_response = client.recv(4096)
    client.close()
    verify_response(server_response)
    assert expected_response in server_response
