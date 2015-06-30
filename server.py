# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket

ADDR = ("127.0.0.1", 8000)

sock = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
)
# sock.setsockopt(
#     socket.SOL_SOCKET,
#     socket.REUSEADDR,
#     1
# )
sock.bind(ADDR)
sock.listen(1)


def response_ok():
    response_headers = 'HTTP/1.1 200 OK\nContent-Type: text/html'
    response_body = '<html><body><h1></h1>\
        <p>All good here, captain.</p></body></html>'

    return response_headers + response_body


def response_error():
    response_headers = ''
    response_body = ''

    return response_headers + response_body

while True:
    try:
        conn, addr = sock.accept()
        msg = ''
        while True:
            msg_recv = conn.recv(16)
            msg += msg_recv
            if len(msg_recv) < 16:
                conn.close()
                break
        print msg
        conn.sendall(response_ok())
    except KeyboardInterrupt:
        break
