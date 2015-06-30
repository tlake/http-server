# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket

addr = ("127.0.0.1", 8000)

"""
Need to refactor headers.
Can use empty list, and then append strings to list, and use '/r/n'.join(list)
Be explicit about using bytestrings
Always use /r/n line terminator
email utils formatdate(usegmt=True) will provide date header formatted correctly
Be sure to count byte length after you have byte string converted from other encoding
Content-Type: text/plain; charset=utf-8

"""


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
                    conn.sendall(response_ok())
                    conn.close()
                    break
            print(msg)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    run_server()
