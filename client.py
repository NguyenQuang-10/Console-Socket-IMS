import socket
import re
import threading


PORT = 5050
HOST = "10.10.45.236"
ADDR = (HOST, PORT)
HEADER = 64
FORMAT = "utf-8"

def is_cmd(string):
    find_cmd_stc = re.compile(r'^![A-Z]+!\s?')
    find = find_cmd_stc.search(string)
    if find:
        return True
    else:
        return False

def Send(msg):
    msg_length = str(len(msg))
    send_length = msg_length.encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    client.send(send_length)
    client.send(msg.encode(FORMAT))


def Recv():
    msg = client.recv(2048).decode(FORMAT)
    if msg:
        return msg

def Recv_var():
    try:
        rm_len = client.recv(HEADER).decode(FORMAT)
        if rm_len:
            rm_len = int(rm_len)
            rm = client.recv(rm_len).decode(FORMAT)
            return rm
    except socket.timeout:
        print("No message recieved")
        pass
def check_usn_format(string):
    usn_format = re.compile(r"^!USN!\s\w+$")
    check = usn_format.search(string)
    if check:
        return True
    else:
        return False


def get_usn():  # doesnt allow extra
    check_usn = True
    while check_usn:
        input_usn = input("Please input your username: ")
        if check_usn_format("!USN! " + input_usn):
            Send("!USN! " + input_usn)
            cf = Recv()
            print(cf)
            if cf == "Succ":
                print("Username have successfully added/changed")
                break
            elif cf == "Fail":  # Cant change username because function is only called at the start
                print("Username is already being use or server failure")
        else:
            print("Username does not fit format")




def to_server():
    print("Output thread started")
    while True:
        user_input = input()
        if is_cmd(user_input):
            if "!DIS!" in user_input:
                Send(user_input)
            elif "!USN!" in user_input:
                continue
            elif "!ONL!" in user_input:
                Send(user_input)
                rm = Recv_var()  # Try except
                if rm:
                    usn_list = rm.split(" ")
                    usn_list.remove("")
                    for usn in usn_list:
                        print(f"\"{usn}\"")
                else:
                    print("No user online")
                continue
            elif "!CON!" in user_input:
                trg_usn = input("Enter the username you want to connect with: ")
                Send("!CON! " + trg_usn)
                re_msg = Recv_var()
                print(re_msg)
                if re_msg == "Succ":
                    print(f"Successfully connected to {trg_usn}")
                elif re_msg == "Fail":
                    print("User doesn't exist")
                continue
        else:
            Send(user_input)
        if user_input == "!DIS!":
            exit()

def from_server():
    print("Input thread started")
    while True:
        print(Recv_var())


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(3)
try:
    client.connect(ADDR)
    print(Recv())
    get_usn()
    while True:
        out_thread = threading.Thread(target=to_server())
        out_thread.start()
        in_thread = threading.Thread(target=from_server())
        in_thread.start()
except ConnectionRefusedError:
    print("[ERROR] Connection Refused | Server is down or connection unstable\n[EC: ConnectionRefusedError]")
    exit()



