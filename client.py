import socket
import re
import threading
import time

PORT = 5055
HEADER = 64
HOST = "10.10.28.246"
ADDR = (HOST, PORT)
FORMAT = "utf-8"
USN_TAG = "!USN!"
ONL_TAG = "!ONL!"
CON_TAG = "!CON!"
MSG_TAG = "!MSG!"
FAIL_BOOL = " FAIL"
SUCC_BOOL = " SUCC"
EXT_TAG = "/EXT/"

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    client.settimeout(10)
except TimeoutError:
    print("[ERROR] Timeout | Can't reach server")
    exit()
socket.setdefaulttimeout(10)

rsp_queue = []

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
    try:
        msg_len = str(len(msg))
        b_msg_len = msg_len.encode(FORMAT)
        b_msg_len = b_msg_len + b' '*(HEADER - len(b_msg_len))
        client.send(b_msg_len)
        client.send(msg.encode(FORMAT))
    except ConnectionResetError:
        print("Server failed")
        exit()


def Recv():
    while True:
        try:
            msg_len = client.recv(HEADER).decode(FORMAT)
            if msg_len:
                msg = client.recv(int(msg_len)).decode(FORMAT)
                return msg
        except socket.timeout:
            pass
        except ConnectionResetError:
            print("Server failed")
            exit()
        except OSError:
            exit()



    # while True:
    #     try:
    #         msg_len = client.recv(HEADER).decode(FORMAT)
    #         if msg_len:
    #             msg = client.recv(int(msg_len)).decode(FORMAT)
    #             return msg
    #     except socket.timeout:
    #         pass
    #     except ValueError:
    #         print("Value Error")
    #         pass


# Add script to add non-rsp to a list and reprint later
def processing(tag, s_bool=None, f_bool=None):
    while True:
        if rsp_queue:
            if s_bool and f_bool:
                if tag + s_bool in rsp_queue:
                    rsp_queue.remove(tag + s_bool)
                    return True
                if tag + f_bool in rsp_queue:
                    rsp_queue.remove(tag + f_bool)
                    return False
            else:
                for rsp in rsp_queue:
                    if tag in rsp:
                        msg = rsp.replace(tag + " ", "")
                        rsp_queue.remove(rsp)
                        if len(msg) > 0:
                            return msg
                        else:
                            return "No user online\n"
    # while True:
    #     rsp = Recv()
    #     if rsp:
    #         print(f'[RECV MSG] {rsp}')  # Delete after debug
    #         if (s_bool is not None) and (f_bool is not None):
    #             if rsp == tag + s_bool:
    #                 return True
    #             elif rsp == tag + f_bool:
    #                 return False
    #         elif tag in rsp:
    #             return rsp.replace(tag + " ", "")

def change_usn():
    input_usn = input("Please input your username: ")
    if check_usn_format("!USN! " + input_usn):
        Send("!USN! " + input_usn)
        print("Sent !USN! " + input_usn)
        if processing(USN_TAG, SUCC_BOOL, FAIL_BOOL):
            print("Username changed")
        else:
            print("Username unavailable")
    else:
        print("Username does not fit format")

def get_usn():
    input_usn = input("Please input your username: ")
    while True:
        if check_usn_format("!USN! " + input_usn):
            Send("!USN! " + input_usn)
            print("Sent !USN! " + input_usn)
            rsp = Recv()
            if rsp == USN_TAG + SUCC_BOOL:
                print("Username created")
                break
            elif rsp == USN_TAG + FAIL_BOOL:
                print("Username unavailable")
                get_usn()
                break
        else:
            print("Username does not fit format")
            get_usn()
            break


def onl_users():
    Send(ONL_TAG)
    print("\n[AVAILABLE USERS]\n" + processing(ONL_TAG))


def send_target():
    input_target = input("Enter the username of the target: ")
    Send(CON_TAG + " " + input_target)
    if processing(CON_TAG, SUCC_BOOL, FAIL_BOOL):
        print("Target selected")
        return True
    else:
        print("Target doesn't exist")
        return False


def disconnect():
    Send('!DIS!')
    print("Exiting...")
    client.close()
    exit()


def handle_msg():
    print("Starting message thread...")
    rsp_queue.clear()
    while True:
        raw_msg = Recv()
        if raw_msg:
            if MSG_TAG in raw_msg:
                msg = raw_msg.replace(MSG_TAG + " ", "")
                print(msg + "\n")
            else:
                rsp_queue.append(raw_msg)


def handle_input():

    target_selected = False

    print("Starting input thread...")
    while True:
        user_input = input()
        if is_cmd(user_input):
            if user_input == "!DIS!":
                disconnect()
            elif user_input == USN_TAG:
                change_usn()
            elif user_input == ONL_TAG:
                onl_users()
            elif user_input == CON_TAG:
                target_selected = send_target()
            else:
                print("Unknown command")
        elif target_selected:
            Send(MSG_TAG + " " + user_input)
        elif not target_selected:
            print("Target not selected")

get_usn()

if __name__ == '__main__':
    threading.Thread(target=handle_msg).start()
    threading.Thread(target=handle_input).start()






