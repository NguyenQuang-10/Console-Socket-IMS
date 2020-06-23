import socket
import re


PORT = 5052
HEADER = 64
HOST = "192.168.1.19"
ADDR = (HOST, PORT)
FORMAT = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def check_usn_format(string):
    usn_format = re.compile(r"^!USN!\s\w+$")
    check = usn_format.search(string)
    if check:
        return True
    else:
        return False


def is_rsp(string):
    find_cmd_stc = re.compile(r'^![A-Z]+!\s[A-Z]+')
    find = find_cmd_stc.search(string)
    if find:
        return True
    else:
        return False


def send(msg):
    msg_len = str(len(msg))
    b_msg_len = msg_len.encode(FORMAT)
    b_msg_len = b_msg_len + b' '*(HEADER - len(b_msg_len))
    client.send(b_msg_len)
    client.send(msg.encode(FORMAT))


def recv():
    msg_len = client.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg = client.recv(int(msg_len)).decode(FORMAT)
        return msg


def get_usn():
    input_usn = input("Please input your username: ")
    while True:
        if check_usn_format("!USN! " + input_usn):
            send("!USN! " + input_usn)
            break
        else:
            print("Username does not fit format")


def fail_usn():
    print("Username unavailable")
    get_usn()


srv_dict = {
    "!USN! SUCC": print("Successfully added Username"),
    "!USN! FAIL": fail_usn(),
}

get_usn()
while True:
    rm = recv()

