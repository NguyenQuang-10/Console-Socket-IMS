import socket
import threading
import re

PORT = 5050
HEADER = 64
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = "!DCN"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def is_cmd(string):
    find_cmd_stc = re.compile(r'^![A-Z]+!\s?')
    find = find_cmd_stc.search(string)
    if find:
        return True
    else:
        return False


def Send(msg, connection):
    msg_length = str(len(msg))
    send_length = msg_length.encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    connection.send(send_length)
    connection.send(msg.encode(FORMAT))


def Recv_var(connection):
    rm_len = connection.recv(HEADER).decode(FORMAT)
    if rm_len:
        rm_len = int(rm_len)
        rm = connection.recv(rm_len).decode(FORMAT)
        return rm


client_dict = {}
usn_dict = {}
usn_list = []


def handle_client(connection, address):
    target = ""
    current_usn = ""
    print(f"{address[0]} has connected")
    connection.send("[CLIENT HAS CONNECTED]".encode(FORMAT))
    while True:
        try:
            msg_length = connection.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = connection.recv(msg_length).decode(FORMAT)
                if is_cmd(msg):
                    if "!DIS!" in msg:
                        client_dict.pop(connection)
                        usn_dict.pop(current_usn)
                        usn_list.remove(current_usn)
                        print(f"{address[0]} disconnected\n")
                        break
                    elif "!USN! " in msg:  # validation of username will happen in client-side
                        usn = msg.replace("!USN! ", "")
                        print("[RECEIVED USN]: " + usn)
                        if usn in usn_list:
                            connection.send("Fail".encode(FORMAT))
                            continue
                        else:
                            if len(current_usn) > 0:
                                usn_list.remove(current_usn)
                            client_dict[connection] = usn
                            usn_dict[usn] = connection
                            usn_list.append(usn)
                            current_usn = usn
                            print(usn_dict)
                            print(client_dict)
                            print(usn_list)
                            connection.send("Succ".encode(FORMAT))
                            continue
                    elif "!ONL!" in msg:
                        name_str = ""
                        for usn in usn_list:
                            if usn != client_dict[connection]:
                                name_str += usn + " "
                        if name_str:
                            Send(name_str,connection)
                        else:
                            Send("", connection)
                    elif "!CON!" in msg:
                        print("Client trying to connect to other clients")
                        r_usn = msg.replace("!CON! ", "")
                        print(r_usn)
                        print(f"{client_dict[connection]} trying to connect with {r_usn}")
                        if (r_usn in usn_list) and (r_usn != current_usn):
                            target = usn_dict[r_usn]
                            Send("Succ", connection)
                        else:
                            Send("Fail", connection)
                            print("User doesn't exist")

                else:
                    if target:
                        Send(msg, target)
                    else:
                        Send("No targer connected", connection)
        except ConnectionResetError:
            client_dict.pop(connection)
            usn_dict.pop(current_usn)
            usn_list.remove(current_usn)
            print(f"{address[0]} disconnected or have crashed\n")
            break
    connection.close()


def start():
    server.listen()
    while True:
        (connection, address) = server.accept()

        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()
        print(f"\n[ACTIVE CONNECTIONS]: {threading.active_count() - 1}")


print("[HOST ADDRESS]: " + HOST)
print("[STARTING SERVER]")
start()
