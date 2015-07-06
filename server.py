# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket
import email
import os
import mimetypes

ADDR = ("127.0.0.1", 8000)
_CRLF = b"\r\n"
_RESPONSE_TEMPLATE = _CRLF.join([
    b"HTTP/1.1 {status_code} {reason_phrase}",
    b"{date}",
    b"Content-Type: {content_type}",
    b"Content-Length: {content_length}",
    "",
    b"{content_body}",
    _CRLF,
])


def setup():
    """
    Create new socket, and bind localhost to socket.
    Set socket to listen, and return socket information.
    """
    sock = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
    )
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(ADDR)
    sock.listen(4)
    return sock


def response_ok(body_plugin, content_type):
    """Zip together arguments for returning an OK response"""

    _date = email.Utils.formatdate(usegmt=True)
    content_body = b"{body_plugin}"
    content_body = content_body.format(body_plugin=body_plugin)

    return _RESPONSE_TEMPLATE.format(
        status_code=b"200",
        reason_phrase=b"OK",
        date=_date,
        content_type=content_type,
        content_length=len(bytes(content_body)),
        content_body=content_body
    )


def response_error(status_code, reason_phrase, body_plugin):
    """Zip together arguments for returning an error response"""

    date = email.Utils.formatdate(usegmt=True)
    content_body = (
        b"<!DOCTYPE html><html><body><p>"
        b"{body_plugin}"
        b"</p></body></html>"
    )
    content_body = content_body.format(body_plugin=body_plugin)

    return _RESPONSE_TEMPLATE.format(
        status_code=status_code,
        reason_phrase=reason_phrase,
        date=date,
        content_type=b'text/html',
        content_length=len(bytes(content_body)),
        content_body=content_body
    )


def parse_request(request):
    client_req = request.split((2 * _CRLF), 1)
    head_chunk = client_req[0].split(_CRLF)
    first_line = head_chunk[0].split()

    host = ''

    for item in head_chunk:
        if "Host: " in item:
            host = item

    if 'GET' != first_line[0]:
        raise NotImplementedError('That is not a valid GET request')
    elif 'HTTP/1.1' != first_line[2]:
        raise NameError('That is not a valid HTTP/1.1 request')
    elif 'Host:' not in host:
        raise ValueError('The required Host header is not present')
    else:
        return first_line[1]


def resolve_uri(parse):
    if '..' in parse:
        raise IOError

    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(here, 'webroot')
    parse = os.path.normpath(parse)
    uri_parts = parse.split('/')
    uri = os.path.join(root, *uri_parts)

    if os.path.isdir(uri):
        body = '<DOCTYPE html><html><body><ul>'

        for file_ in os.listdir(uri):
            body += '<li>' + file_ + '</li>'

        body += '</ul></body></html>'
        content_type = 'text/html'

    elif os.path.isfile(root + parse):
        with open(uri, 'rb') as file_:
            body = file_.read()

        content_type = mimetypes.guess_type(uri)[0]

    else:
        raise IOError

    return body, content_type


def run_server():
    """
    Create new instance of server, and begin accepting, logging,
    and returning response.
    """
    server = setup()
    while True:
        try:
            conn, addr = server.accept()
            accum = []
            while True:
                """
                If response in msg, can use this to return Ok or Error
                """
                request_part = conn.recv(512)
                accum.append(request_part)
                if len(request_part) < 512:
                    break

            msg = b''.join(accum)
            print(msg)

            try:
                parsed_response = parse_request(msg)
                body, content_type = resolve_uri(parsed_response)
                # import pdb; pdb.set_trace()
                server_response = response_ok(body, content_type)

            except NotImplementedError:
                server_response = response_error(
                    b"405",
                    b"Method Not Allowed",
                    b"GET method required."
                )

            except NameError:
                server_response = response_error(
                    b"400",
                    b"Bad Request",
                    b"Not a valid HTTP/1.1 request."
                )

            except ValueError:
                server_response = response_error(
                    b"406",
                    b"Not Acceptable",
                    b"'Host' header required."
                )

            except IOError:
                server_response = response_error(
                    b"404",
                    b"Not Found",
                    b"Requested resource does not exist."
                )

            conn.sendall(server_response)
            conn.close()

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    run_server()
