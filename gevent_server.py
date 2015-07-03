# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import email
import os
import sys
import mimetypes

addr = ("127.0.0.1", 8000)
_CRLF = b"\r\n"
_RESPONSE_TEMPLATE = _CRLF.join([
    b"HTTP/1.1 {status_code} {reason_phrase}",
    b"{date}",
    b"Content-Type: {content_type}",
    b"Content-Length: {content_length}",
    b"",
    b"<html><body><p>{content_body}</p></body></html>",
    b"",
])


def response_ok(_body, _type):
    """Zip together arguments for returning an OK response"""

    _date = email.Utils.formatdate(usegmt=True)

    return _RESPONSE_TEMPLATE.format(
        status_code=b"200",
        reason_phrase=b"OK",
        date=_date,
        content_type=_type,
        content_length=str(sys.getsizeof(_body)),
        content_body=_body
    )


def response_error(status_code, reason_phrase, content_body):
    """Zip together arguments for returning an error response"""

    date = email.Utils.formatdate(usegmt=True)

    return _RESPONSE_TEMPLATE.format(
        status_code=status_code,
        reason_phrase=reason_phrase,
        date=date,
        content_type=b'text/plain',
        content_length=str(sys.getsizeof(content_body)),
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
    elif 'Host: ' not in host:
        raise ValueError('The required Host header is not present')
    else:
        return first_line[1]


def resolve_uri(parse):
    root = os.path.join(os.getcwd(), 'webroot')
    body = ''
    content_type = ''
    if os.path.isdir(os.path.join(root, parse)):
        body = '<!DOCTYPE html><html><body><ul>'
        for file_ in os.listdir(root + parse):
            body += '<li>' + file_ + '</li>'
        body += '</ul></body></html>'
        content_type = 'text/html'
    elif os.path.isfile(root + parse):
        with open((root + parse), 'rb') as file_:
            body = file_.read()
        content_type, encoding = mimetypes.guess_type(parse)
    else:
        raise IOError
    return (body, content_type)


def echo(socket, address):
    """
    Create new instance of server, and begin accepting, logging,
    and returning response.
    """
    buffsize = 1024
    msg = ''
    # Better to use a list and then join.
    while True:
        """
        If response in msg, can use this to return Ok or Error
        """
        msg_recv = socket.recv(buffsize)
        msg += msg_recv
        if len(msg_recv) < buffsize:
            try:
                parsed_response = parse_request(msg)
                body, content_type = resolve_uri(parsed_response)
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
            socket.sendall(server_response)
            socket.close()
            break
    print(msg)


def run_gevent_server():
    from gevent.server import StreamServer
    from gevent.monkey import patch_all
    patch_all()
    gserver = StreamServer(('127.0.0.1', 8000), echo)
    print("starting server")
    gserver.serve_forever()


if __name__ == '__main__':
    run_gevent_server()
