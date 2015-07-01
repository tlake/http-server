# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket
import email

addr = ("127.0.0.1", 8000)
date = email.Utils.formatdate(usegmt=True)


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
    response_headers = (
        b'HTTP/1.1 200 OK\r\n'
        + date +
        b'Content-Type: text/html\r\n'
        b'Content-Length:\r\n')

    response_body = (
        b'<html><body>'
        b'<p>All good here, captain.</p>'
        b'</body></html>')

    return response_headers + response_body


def response_error(header, text):
    """Return Header and Body information for three types of errors"""

    response_headers = (
        header +
        date +
        b'Content-Type: text/html\r\n'
        b'Content-Length:\r\n')

    response_body = (
        b'<html><body>'
        b'<p>' + text + '</p>'
        b'</body></html>')

    return response_headers + response_body


def parse_request(request):
    client_req = request.split('\r\n')
    meth = client_req[0].split(' ')
    host = ''
    for item in client_req:
        if "Host: " in item:
            host = item

    if 'GET' != meth[0]:
        raise NotImplementedError('That is not a valid GET request')
    elif 'HTTP/1.1' != meth[2]:
        raise NameError('That is not a valid HTTP/1.1 request')
    elif 'Host: ' not in host:
        raise ValueError('The required Host header is not present')
    else:
        return meth[1]


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
                    # import pdb; pdb.set_trace()
                    try:
                        client_response = parse_request(msg)
                    except NotImplementedError:
                        client_response = response_error(
                            "HTTP/1.1 405 Method Not Allowed\r\n",
                            "GET method required.\r\n"
                        )
                    except NameError:
                        client_response = response_error(
                            "HTTP/1.1 400 Bad Request\r\n",
                            "Not a valid HTTP/1.1 request.\r\n"
                        )
                    except ValueError:
                        client_response = response_error(
                            "HTTP/1.1 406 Not Acceptable\r\n",
                            "'Host' header required.\r\n"
                        )
                    conn.sendall(client_response)
                    conn.close()
                    break
            print(msg)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    run_server()
