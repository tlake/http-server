import socket

addr = ("127.0.0.1", 8000)


def client_setup():
    """
    Create new client sockets, and connect to localhost address.
    """
    client = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
    )
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.connect(addr)

    return client


def run_client():
    """Create new instance of client, and send/receive request/response."""
    cli = client_setup()
    msg = b"GET webroot/ HTTP/1.1\r\nHost: www.team.com:80\r\n\r\n"
    try:
        cli.sendall(msg)
        while True:
            part = cli.recv(4096)
            cli.shutdown(socket.SHUT_WR)
            print(part)
            if len(part) < 4096:
                cli.close()
                break
    except Exception as e:
        print(e)


if __name__ == "__main__":
    run_client()
