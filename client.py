import socket
import re


PORT = 5050
HEADER = 64
HOST = "192.168.1.19"
ADDR = (HOST, PORT)
FORMAT = "utf-8"
USN_TAG = "!USN!"
FAIL_BOOL = " FAIL"
SUCC_BOOL= " SUCC"

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


def is_cmd(string):
    find_cmd_stc = re.compile(r'^![A-Z]+!')
    find = find_cmd_stc.search(string)
    if find:
        return True
    else:
        return False


def Send(msg):
    msg_len = str(len(msg))
    b_msg_len = msg_len.encode(FORMAT)
    b_msg_len = b_msg_len + b' '*(HEADER - len(b_msg_len))
    client.send(b_msg_len)
    client.send(msg.encode(FORMAT))


def Recv():
    msg_len = client.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg = client.recv(int(msg_len)).decode(FORMAT)
        return msg


def get_usn():
    input_usn = input("Please input your username: ")
    while True:
        if check_usn_format("!USN! " + input_usn):
            Send("!USN! " + input_usn)
            print("Sent !USN! " + input_usn)
            validate_usn = True
            while validate_usn:
                rm = Recv()
                print(rm)
                if rm == USN_TAG + SUCC_BOOL:
                    print(rm)
                    print("Username created/changed")
                    break
                elif rm == USN_TAG + FAIL_BOOL:
                    print("Username unavailable")
                    get_usn()
            break
        else:
            print("Username does not fit format")


def disconnect():
    Send('!DIS!')
    print("Exiting...")
    client.close()
    exit()


def handle_input():
    user_input = input()
    if is_cmd(user_input):
        if user_input == "!DIS!":
            disconnect()
        if user_input == USN_TAG:
            get_usn()


get_usn()
""" Exist as debug only
    Will exist as threads in the future
"""
while True:
    handle_input()

