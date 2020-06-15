import socket
import re

PORT = 5050
HOST = "10.10.46.0"
ADDR = (HOST, PORT)
HEADER = 64
FORMAT = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect(ADDR)
except ConnectionRefusedError:
    print("[ERROR] Connection Refused | Server is down or connection unstable\n[EC: ConnectionRefusedError]")
    exit()


def Send(msg):
    msg_length = str(len(msg))
    send_length = msg_length.encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    client.send(send_length)
    client.send(msg.encode(FORMAT))


def Recv():
    msg = client.recv(2048).decode(FORMAT)
    if msg: print(msg)


def check_usn_format(string):
    usn_format = re.compile(r"^!USN!\s\w+$")
    check = usn_format.search(string)
    if check:
        return True


def get_usn():
    input_usn = input("Please input your username: ")
    if check_usn_format("!USN! " + input_usn):
        client.send(("!USN! " + input_usn).encode(FORMAT))
    else:
        print("Username does not fit format")
    validating = True
    while validating:


Recv()
Send("[CLIENT HAS CONNECTED]")
get_usn()
while True:
    user_input = input("")
    Send(user_input)
    if user_input == "!DIS!":
        exit()
