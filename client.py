import socket
import re

PORT = 5050
HOST = "192.168.1.17"
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
    else:
        return False


def get_usn():
    input_usn = input("Please input your username: ")
    if check_usn_format("!USN! " + input_usn):
        Send("!USN! " + input_usn)
    else:
        print("Username does not fit format")
    validating = True
    while validating:
        cf = client.recv(2048).decode(FORMAT)
        if cf == "Succ":
            print("Username have successfully added/changed")
            break
        elif cf == "Fail": # Cant change username because function is only called at the start
            print("Username is already being use")
            ask_again = input("Do you want to try again? [Y/N] ")
            if ask_again == "Y":
                get_usn()
                break
            elif ask_again == "N":
                break
            else:
                print("Invalid Input")
                pass

Recv()
Send("[CLIENT HAS CONNECTED]")
get_usn()
while True:
    user_input = input("")
    Send(user_input)
    if user_input == "!DIS!":
        exit()
