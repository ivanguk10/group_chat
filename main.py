import _thread
import os
import socket
import struct

import random

name = ""
rang = ""
message = ""
chat_identifier = ""
group_name = ""
multicast_group = ("233.2.29.34", 0)
global mysocket
waiting = ""


def recieveMessage():
    global recv_message
    global addres
    global mysocket
    while True:
        recv_message = mysocket.recv(1024)
        addres = mysocket.recv(1024)
        message = str(recv_message.decode('utf-8'))

        if rang == "Admin":
            print("<", message.split('\n')[0], ">", ": ", message.split('\n')[1], sep="")

            if message.find != "wait":
                mysocket.sendto(message.encode("utf-8"), multicast_group)
            else:
                print("".join(["Add user: ", message.split('\n')[0], "? [YES/NO] "]))
                waiting = f'{rang} \n{message} \n {addres}'
        else:
            if name != message.split('\n')[0]:
                print("<", message.split('\n')[0], ">", ": ", message.split('\n')[1], sep="")


def sendMessage():
    global check_string
    global state
    global recv_message
    global addres
    global chat_identifier
    global mysocket
    global rang
    global waiting
    global passing

    while True:
        try:
            message = input()
            passing = f'{message} \n{name}'
            chat_identifier = int(input("Enter identifier: "))
            mysocket.sendto(passing.encode("utf-8"), ("", chat_identifier))
            recv_message = mysocket.recv(1024)
            addres = mysocket.recv(1024)
            if rang == "Admin":
                if waiting:
                    message, addres = (
                        "message",
                        "addres",
                    )

                    state = False
                    check_string = f'{name} \n{message} \n{multicast_group[-1]}' \
                                   f'\n{group_name} \n{state}'

                    if message == "NO":
                        mysocket.sendto(
                            check_string.encode("utf-8"), addres
                        )
                    else:
                        print(f"User {message.split[0]} join chat!")
                        state = True
                        mysocket.sendto(
                            check_string.encode("utf-8"), addres
                        )

                    waiting = ''
                else:
                    mysocket.sendto(check_string.encode("utf-8"), multicast_group)
            else:
                mysocket.sendto(
                    passing.encode("utf-8"), ("", chat_identifier)
                )
        except Exception:
            continue

# главная функция
def main():
    global mysocket
    global multicast_group
    global group_name
    global chat_identifier
    global passing
    global data
    global addres
    global rang
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print('*************************************************')
    print('*  You are welcome in our group_chat!!!        *')
    print('*  Чтобы выйти, отправьте сообщение: Выход()    *')

    print('*************************************************')

    global name
    name = ''
    while True:
        if not name:
            name = input('Enter name: ')
            if not name:
                print('Enter not empty name!')
            else:
                break

    print('Choose option')
    print('1. Create chat')
    print('2. Join chat')
    print('3. Exit')
    while True:
        option = int(input())
        if option == 1:
            rang = "Admin"
            ttl = struct.pack("b", 1)
            mysocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            multicast_group = (multicast_group[0], random.randint(10000, 20000))
            group_name = input("Enter your group name: ")
            mysocket.sendto("".encode("utf-8"), multicast_group)
            print("Identifier: ", mysocket.getsockname()[-1])
        elif option == 2:
            rang = "User"
            accept = f'{name} \n wait \n can i join to your group'
            chat_identifier = int(input("Enter identifier: "))
            mysocket.sendto(accept.encode("utf-8"), ("", chat_identifier))
            data, addres = str(mysocket.recv(1024))
            if data.find(''):
                print(f"You join {group_name} chat")
                mysocket.close()
                multicast_group = (multicast_group[0], multicast_group[-1])
                mysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                mysocket.bind(multicast_group)
                mreq = struct.pack(
                    "4sL", socket.inet_aton(multicast_group[0]), socket.INADDR_ANY
                )
                mysocket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            else:
                print('You can not join ')
        elif option == 3:
            os._exit(1)
        else:
            print('make correct choice')

        _thread.start_new_thread(recieveMessage, ())

        sendMessage()

        print('*************************************************')


if __name__ == '__main__':
    main()
