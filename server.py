import socket
import threading

PORT = 5052
HEADER = 64
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
FORMAT = "utf-8"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def send(msg, conn):
    msg_len = str(len(msg))
    b_msg_len = msg_len.encode(FORMAT)
    b_msg_len = b_msg_len + b' '*(HEADER - len(b_msg_len))
    conn.send(b_msg_len)
    conn.send(msg.encode(FORMAT))


def recv(conn):
    msg_len = conn.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg = conn.recv(int(msg_len)).decode(FORMAT)
        return msg


def handle_client(conn, addr):
    print(f"{addr} connected")
    while True:
        msg_len = conn.recv(HEADER).decode(FORMAT)
        if msg_len:
            msg = conn.recv(int(msg_len)).decode(FORMAT)
            print(msg)


def start():
    server.listen()
    while True:
        (conn, addr) = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


print(f"[START] STARTING AT {HOST}")
start()