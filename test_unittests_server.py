# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import server
import pytest


################
# UNIT TESTS
################


def test_response_ok():
    response = server.response_ok(b"123456789", "text/plain")
    assert "text/plain" in response
    assert '46' in response


def test_response_error():
    response = server.response_error(
        b"HTTP/1.1 405 Method Not Allowed\r\n",
        b"GET method required.\r\n"
    )
    assert b"GET method required" in response
    assert b"text/html" in response
    assert b"</body>" in response


def test_parse_request_rejects_non_get():
    with pytest.raises(NotImplementedError):
        server.parse_request(
            b"POST / HTTP/1.1\r\n"
            b"Host: http://example.com\r\n"
            b"\r\n"
        )


def test_parse_request_rejects_non_http_1_1():
    with pytest.raises(Exception):
        server.parse_request(
            b"GET / HTTP/1.0\r\n"
            b"Host: http://example.com\r\n"
            b"\r\n"
        )


def test_parse_request_rejects_absent_host_header():
    with pytest.raises(ValueError):
        server.parse_request(
            b"GET / HTTP/1.1\r\n"
            b"Some bullshit header\r\n"
            b"Another shitty header\r\n"
            b"\r\n"
        )


def test_parse_request_returns_validated_request():
    valid_request = (
        b"GET /heres/the/URI HTTP/1.1\r\n"
        b"Host: www.example.com\r\n"
        b"\r\n"
        b"blah blah some kind of body\r\n"
        b"\r\n"
    )
    assert b"/heres/the/URI" == server.parse_request(valid_request)


def test_resolve_uri_success():
    body, content_type = server.resolve_uri(b'/sample.txt')
    assert b"simple text file" in body
    assert b"text" in content_type


def test_resolve_uri_failure():
    with pytest.raises(OSError):
        server.resolve_uri(b"laskjdhfku")
