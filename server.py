import socket
import threading
import re

# CONSTANTS
PORT = 5050
HEADER = 64
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
FORMAT = "utf-8"
USN_TAG = "!USN!"
FAIL_BOOL = " FAIL"
SUCC_BOOL= " SUCC"

# UNIVERSAL VARIABLES
usn_dict = {}
cli_list = []
usn_list = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def is_rsq(string):
    if string:
        find_cmd_stc = re.compile(r'^![A-Z]+!\s\w+')
        find = find_cmd_stc.search(string)
        if find:
            return True
        else:
            return False


def find_cmd(string):
    find_cmd_stc = re.compile(r'^![A-Z]+!')
    find = find_cmd_stc.findall(string)
    if find:
        return find[0]
    else:
        return None


def Send(msg, conn):
    msg_len = str(len(msg))
    b_msg_len = msg_len.encode(FORMAT)
    b_msg_len = b_msg_len + b' '*(HEADER - len(b_msg_len))
    conn.send(b_msg_len)
    conn.send(msg.encode(FORMAT))


def Recv(conn):
    msg_len = conn.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg = conn.recv(int(msg_len)).decode(FORMAT)
        return msg


def val_usn(usn_msg, conn):
    print("Validating Username")
    usn = usn_msg.replace(USN_TAG + " ", "")
    print(usn)
    if conn not in cli_list or usn not in usn_list:
        usn_dict[usn] = conn
        usn_list.append(usn)
        cli_list.append(conn)
        Send(USN_TAG + SUCC_BOOL, conn)
    else:
        Send(USN_TAG + FAIL_BOOL, conn)


cmd_dict = {
    USN_TAG: val_usn,
}


def handle_client(conn, addr):
    print(f"{addr} connected")
    while True:
        rm = Recv(conn)
        if rm:
            print(f"[RECV_RAW] {rm}")
        if is_rsq(rm):
            cmd = find_cmd(rm)
            print(cmd)
            # cmd_dict[cmd](rm, conn)


def start():
    server.listen()
    while True:
        (conn, addr) = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


print(f"[START] STARTING AT {HOST}")
start()