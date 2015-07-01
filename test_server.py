import server
import socket
import pytest
from multiprocessing import Process


@pytest.yield_fixture(scope='session')
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


# def test_client_ok_response(client_setup):
#     ok_resp = server.response_ok()
#     client_setup.sendall(ok_resp)
#     server_response = client_setup.recv(4096)
#     expected_response = 'All good here, captain.'
#     assert expected_response in server_response


# def test_server_rejects_non_get(client_setup):
#     client = client_setup
#     client.sendall(b'Not a proper GET for sure.')
#     expected_response = (
#         b"HTTP/1.1 405 Method Not Allowed\r\n"
#         b"Host: localhost:8000\r\n"
#     )
#     response = client.recv(4096)
#     assert expected_response in response


# def test_server_rejects_non_http_1_1(client_setup):
#     client = client_setup
#     client.sendall('GET butstillwrong HTTP/1.0')
#     expected_response


################
# TESTS REGARDING parse_request
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


# Update your response_error function to parameterize the error code and
# reason phrase.


# The return value should still be a well-formed HTTP error response, with the
# passed error code and reason phrase.
# Update the server loop you built for step one
# pass the request you accumulate into your new parse_request function
# handle any errors raised by building an appropriate HTTP error response
# if no errors are raised, build an HTTP 200 OK response.
# return the response you built to the client
