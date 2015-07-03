# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import email
import os
import mimetypes

addr = ("127.0.0.1", 8000)
date = email.Utils.formatdate(usegmt=True)
_CRLF = b"\r\n"


def response_ok(_body, _type):
    """
    Ensure that the body of the requested resource is returned in a "200 OK"
    response.

    The response should include the appropriate header to indicate the type
    of resource being returned.

    The response should also include the appropriate header to indicate the
    amount of content being returned.

    The response should include any other valid HTTP headers you wish to add.

    You will update your response_ok function to accomplish this task.
    """

    _RESPONSE_TEMPLATE = _CRLF.join([
        b"HTTP/1.1 200 OK",
        b"{date}",
        b"Content-Type: {content_type}",
        b"Content-Length: {content_length}",
        b"",
        b"{content_body}",
        b"",
    ])

    _RESPONSE_TEMPLATE

    return _RESPONSE_TEMPLATE.format(
        date=date,
        content_type=_type,
        content_length='something',
        content_body=_body
    )


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
    """
    NOTES:

    Use `.split(< 2 CRLF's >, 1)` to separate the header chunk from the
    body chunk, since they must always be separated by two CRLFs.
    Additionally, the second optional argument to .split() is the number
    of times to split. This way, we avoid dealing with a situation where
    the body contains double CRLFs.

    Then, for processing headers, use .split() without args, which will
    strip at *any* intersituated whitespace, whereas .split(' ') will
    split at *each individual* whitespace.
    """
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


def resolve_uri(parse):
    root = os.path.join(os.getcwd(), 'webroot')
    body = ''
    content_type = ''
    if os.path.isdir(root + parse):
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
        raise OSError
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
            except NotImplementedError:
                client_response = response_error(
                    b"HTTP/1.1 405 Method Not Allowed\r\n",
                    b"GET method required.\r\n"
                )
            except NameError:
                client_response = response_error(
                    b"HTTP/1.1 400 Bad Request\r\n",
                    b"Not a valid HTTP/1.1 request.\r\n"
                )
            except ValueError:
                client_response = response_error(
                    b"HTTP/1.1 406 Not Acceptable\r\n",
                    b"'Host' header required.\r\n"
                )
            except OSError:
                client_response = response_error(
                    b"HTTP/1.1 420 Enhance Your Calm\r\n",
                    b"Keyboard Driver Error\r\n"
                )
            client_response = response_ok(body, content_type)
            socket.sendall(client_response)
            socket.close()
        else:
            break
    print(msg)


if __name__ == '__main__':
    from gevent.server import StreamServer
    from gevent.monkey import patch_all
    patch_all()
    gserver = StreamServer(('127.0.0.1', 8000), echo)
    print("starting server")
    gserver.serve_forever()
