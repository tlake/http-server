import socket


def client_setup():
    addr = ("127.0.0.1", 8000)
    # Check the python socket documentation for a way to avoid the
    # 'addr already in use' error

    client = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
    )
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.connect(addr)

    return client


def run_client():
    cli = client_setup()
    msg = "do you hear me?"
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
