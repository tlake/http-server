# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import server
import socket
import pytest
import time
from multiprocessing import Process


addr = ("127.0.0.1", 8000)


@pytest.yield_fixture(scope='module', autouse=True)
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


def test_client_receives_ok_on_image_request(client_setup):
    client = client_setup
    client.sendall(
        b"GET /images/sample_1.png HTTP/1.1\r\n"
        b"Host: www.host.com:80\r\n"
        b"\r\n"
    )
    ok_header = b"HTTP/1.1 200 OK"
    server_response = client.recv(4096)
    client.close()
    assert ok_header in server_response


def test_client_receives_ok_on_textfile_request(client_setup):
    client = client_setup
    client.sendall(
        b"GET /sample.txt HTTP/1.1\r\n"
        b"Host: www.host.com:80\r\n"
        b"\r\n"
    )
    ok_header = b"HTTP/1.1 200 OK"
    server_response = client.recv(4096)
    client.close()
    assert ok_header in server_response


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
    assert text in server_response


def test_client_receives_root_filesystem(client_setup):
    client = client_setup
    client.sendall(b"GET / HTTP/1.1\r\nHost: www.host.com:80\r\n\r\n")
    expected_response = (
        '<!DOCTYPE html><html>'
        '<body><ul><li>a_web_page.html</li>'
        '<li>sample.txt</li><li>make_time.py</li>'
        '<li>images</li>'
        '</ul></body></html>'

    )
    server_response = client.recv(4096)
    client.close()
    assert expected_response in server_response


def test_client_receives_error_on_not_get(client_setup):
    client = client_setup
    client.sendall(b"DELETE / HTTP/1.1\r\nHost: www.host.com:80\r\n\r\n")
    expected_response = (b"405 Method Not Allowed")
    server_response = client.recv(4096)
    client.close()
    assert expected_response in server_response
