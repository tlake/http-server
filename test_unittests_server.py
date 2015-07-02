# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import server
import pytest


################
# UNIT TESTS
################


# Implement a function called parse_request
# The function should take a single argument which is the request from the
# client. The function should only accept GET requests, any other request
# should raise an appropriate Python error
def test_parse_request_rejects_non_get():
    with pytest.raises(NotImplementedError):
        server.parse_request(
            b"POST / HTTP/1.1\r\n"
            b"Host: http://example.com\r\n"
            b"\r\n"
        )


# The function should only accept HTTP/1.1 requests, a request of any other
# protocol should raise an appropriate Python error
def test_parse_request_rejects_non_http_1_1():
    with pytest.raises(Exception):
        server.parse_request(
            b"GET / HTTP/1.0\r\n"
            b"Host: http://example.com\r\n"
            b"\r\n"
        )


# The function should validate that a proper Host header was included in the
# request, if not, raise an appropriate Python error
def test_parse_request_rejects_absent_host_header():
    with pytest.raises(ValueError):
        server.parse_request(
            b"GET / HTTP/1.1\r\n"
            b"Some bullshit header\r\n"
            b"Another shitty header\r\n"
            b"\r\n"
        )


# If none of the conditions above arise, then the function should return the
# URI from the clients request
def test_parse_request_returns_validated_request():
    valid_request = (
        b"GET /heres/the/URI HTTP/1.1\r\n"
        b"Host: www.example.com\r\n"
        b"\r\n"
        b"blah blah some kind of body\r\n"
        b"\r\n"
    )
    assert b"/heres/the/URI" == server.parse_request(valid_request)
