import socket
import re


PORT = 5050
HEADER = 64
HOST = "10.10.44.78"
ADDR = (HOST, PORT)
FORMAT = "utf-8"
USN_TAG = "!USN!"
ONL_TAG = "!ONL!"
CON_TAG = "!CON!"
FAIL_BOOL = " FAIL"
SUCC_BOOL = " SUCC"

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
    find_cmd_stc = re.compile(r'^![A-Z]+!$')
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


# Add script to add non-rsp to a list and reprint later
def processing(tag, s_bool=None, f_bool=None):
    while True:
        rm = Recv()
        print(f'[RECV MSG] {rm}')  # Delete after debug
        if (s_bool is not None) and (f_bool is not None):
            if rm == tag + s_bool:
                return True
            elif rm == tag + f_bool:
                return False
        elif tag in rm:
            return rm.replace(tag + " ", "")

def get_usn():
    input_usn = input("Please input your username: ")
    while True:
        if check_usn_format("!USN! " + input_usn):
            Send("!USN! " + input_usn)
            print("Sent !USN! " + input_usn)
            if processing(USN_TAG, SUCC_BOOL, FAIL_BOOL):
                print("Username created/change")
            else:
                print("Username unavailable")
                get_usn()
            break
        else:
            print("Username does not fit format")


def onl_users():
    Send(ONL_TAG)
    print("\n[AVAILABLE USERS]\n" + processing(ONL_TAG))


def send_target():
    input_target = input("Enter the username of the target: ")
    Send(CON_TAG + " " + input_target)
    if processing(CON_TAG, SUCC_BOOL, FAIL_BOOL):
        print("Target selected")
    else:
        print("Target doesn't exist")


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
        elif user_input == USN_TAG:
            get_usn()
        elif user_input == ONL_TAG:
            onl_users()
        elif user_input == CON_TAG:
            send_target()
        else:
            print("Unknown command")

get_usn()
""" Exist as debug only
    Will exist as threads in the future
"""
while True:
    handle_input()

