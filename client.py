import socket
import re


PORT = 5050
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
                if "!USN!" in rm:
                    print(rm)
                    srv_dict[rm]()  # Pycharm is dumb, it shows this when you try to call a function from a dictionary
                    break
                else:
                    pass
        else:
            print("Username does not fit format")


def fail_usn(): # Python recognize the functions as part of the command and execute them on start
    print("Username unavailable")
    get_usn()


srv_dict = {
    "!USN! SUCC": print("Successfully added Username"),
    "!USN! FAIL": fail_usn(),
}

get_usn()
print("TERMINATING")
