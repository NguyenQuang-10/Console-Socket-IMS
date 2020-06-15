import socket
import threading
import re

PORT = 5050
HEADER = 64
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = "!DCN"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def is_cmd(string):
    find_cmd_stc = re.compile(r'^![A-Z]+!\s?')
    find = find_cmd_stc.search(string)
    if find:
        return True
    else:
        return False


def handle_client(connection, address):
    print(f"{address[0]} has connected")
    connection.send("[CLIENT HAS CONNECTED]".encode(FORMAT))
    while True:
        try:
            msg_length = connection.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = connection.recv(msg_length).decode(FORMAT)
                if is_cmd(msg):
                    if "!DIS!" in msg:
                        print(f"{address[0]} disconnected\n")
                        break
                    elif "!USN! " in msg:
                        pass  # validation of username will happen in client-side
                else:
                    print(msg)
        except ConnectionResetError:
            print(f"{address[0]} disconnected or have crashed\n")
            break
    connection.close()


def start():
    server.listen()
    while True:
        (connection, address) = server.accept()
        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()
        print(f"\n[ACTIVE CONNECTIONS]: {threading.active_count() - 1}")


print("[HOST ADDRESS]: " + HOST)
print("[STARTING SERVER]")
start()