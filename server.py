# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket

addr = ("127.0.0.1", 8000)


def setup():
    """
    Create new socket, and bind localhost to socket.
    Set socket to listen, and return socket information.
    """
    sock = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
    )
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(addr)
    sock.listen(1)
    return sock


def response_ok():
    """Return Header and Body information for Response 200."""
    response_headers = 'HTTP/1.1 200 OK\nContent-Type: text/html'
    response_body = '<html><body><h1></h1>'\
        '<p>All good here, captain.</p></body></html>'

    return response_headers + response_body


def response_error():
    """Return Header and Body information for Response 500."""
    response_headers = ('HTTP/1.1 500 Internal Server Error\r\n'
                        'Content-Type: text/html\r\n'
                        )
    response_body = '<html><body><h1></h1>'\
        '<p>Your server no bueno.</p></body></html>'

    return response_headers + response_body


def parse_request(request):
    client_req = request.split('\r\n')
    meth = ''
    host = ''
    uri = ''
    for item in client_req:
        if 'GET /' in item:
            meth = item
            meth = meth.split(' ')
        if "Host: " in item:
            host = item
        if '/' in item:
            uri = item

    if 'GET' not in meth:
        raise NotImplementedError('That is not a valid GET request')
    elif 'HTTP/1.1' not in meth:
        raise Exception('That is not a valid HTTP/1.1 request')
    elif 'Host: ' not in host:
        raise ValueError('The required Host header is not present')
    else:
        return uri


def run_server():
    """
    Create new instance of server, and begin accepting, logging,
    and returning response.
    """
    server = setup()
    while True:
        try:
            conn, addr = server.accept()
            msg = ''
            while True:
                """
                If response in msg, can use this to return Ok or Error
                """
                msg_recv = conn.recv(4096)
                msg += msg_recv
                if len(msg_recv) < 4096:
                    parsed_response = ''
                    conn.sendall(parsed_response)
                    conn.close()
                    break
            print(msg)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    run_server()
