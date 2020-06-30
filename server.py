import socket
import threading
import re

# CONSTANTS
PORT = 5055
HEADER = 64
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
FORMAT = "utf-8"
USN_TAG = "!USN!"
CON_TAG = "!CON!"
FAIL_BOOL = " FAIL"
SUCC_BOOL= " SUCC"
MSG_TAG = "!MSG!"

# UNIVERSAL VARIABLES
usn_dict = {}
usn_list = []

sending_rsp = {

}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def is_rsq(string):
    if string:
        find_cmd_stc = re.compile(r'^![A-Z]+!?\s?\w+')
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
    sending_rsp[conn] = True
    for i in range(0,1):
        msg_len = str(len(msg))
        b_msg_len = msg_len.encode(FORMAT)
        b_msg_len = b_msg_len + b' '*(HEADER - len(b_msg_len))
        conn.send(b_msg_len)
        conn.send(msg.encode(FORMAT))
        print(f"Sent {msg}")
    sending_rsp[conn] = False


def Recv(conn):
    msg_len = conn.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg = conn.recv(int(msg_len)).decode(FORMAT)
        return msg


# Handle username requests
"""Note:
    Changing username to old/existed username is possible and is not prevented
"""


def val_usn(usn_msg, conn):
    print("Validating Username")
    usn = usn_msg.replace(USN_TAG + " ", "")
    print("[INPUT USERNAME]: " + usn)
    if (usn not in usn_list) and (usn is not None):
        usn_dict[usn] = conn
        usn_list.append(usn)
        print(usn_list)
        Send(USN_TAG + SUCC_BOOL, conn)
        return usn
    else:
        Send(USN_TAG + FAIL_BOOL, conn)


def rmv_usr(current_usn, conn):
    usn_dict.pop(current_usn)
    usn_list.remove(current_usn)


def list_global_var():  # handle command from server
    print(f"[AVAILABLE USERS] {usn_list}")
    print(f"[AVAILABLE CLIENTS] {usn_dict}")


def handle_client(conn, addr):
    sending_rsp[conn] = False

    print(f"{addr} connected")

    target = ""
    cli_usn = ""

    while True:
        rm = Recv(conn)
        if rm:
            print(f"[RECV_RAW] {rm}")
        if is_rsq(rm):
            cmd = find_cmd(rm)
            print("[RECV CMD] "+cmd)
            if cmd == USN_TAG:
                if cli_usn:  # validate if user have username or not
                    rmv_usr(cli_usn, conn)
                    cli_usn = val_usn(rm, conn)  # Client have username already
                else:
                    cli_usn = val_usn(rm, conn)
            elif cmd == "!DIS!":
                rmv_usr(cli_usn, conn)
                print(f"User {cli_usn} has disconnected")
                list_global_var()
                break
            elif cmd == "!ONL!":
                usn_str = ""
                for usn in usn_list:
                    if usn != cli_usn:
                        usn_str += usn + "\n"
                Send(("!ONL! " + usn_str), conn)
            elif cmd == CON_TAG:
                rcv_trg = rm.replace(CON_TAG + " ", "")
                if rcv_trg in usn_list and rcv_trg != cli_usn:
                    target = rcv_trg
                    Send(CON_TAG + SUCC_BOOL, conn)
                    print(f"Connected to {target}")
                else:
                    Send(CON_TAG + FAIL_BOOL, conn)
            elif cmd == MSG_TAG:
                msg = rm.replace(MSG_TAG + " ", "")
                try:
                    if target:
                        target_cli = usn_dict[target]
                        while True:
                            if not sending_rsp[usn_dict[target]]:
                                Send(MSG_TAG + " " + f"\"{cli_usn}: {msg}\"", target_cli)
                                break
                except KeyError:
                    Send(MSG_TAG + " Targeted user have disconnected, changed name, or don't exist", conn)
            list_global_var()
    conn.close()


def start():
    server.listen()
    while True:
        (conn, addr) = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


print(f"[START] STARTING AT {HOST}")
start()