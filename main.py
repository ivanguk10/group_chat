import os
import socket
import sys
from threading import Thread
import time

global list_admin_chats
list_admin_chats = list()


class group_chat:
    def __init__(self, name, port, is_blocked, is_admin):
        self.name = name
        self.port = port
        self.is_blocked = is_blocked
        self.is_admin = is_admin

def GetUdpChatMessage():
    global name
    global broadcastSocket
    global current_online
    global port
    global list_admin_chats

    while True:
        recv_message = broadcastSocket.recv(1024)  # получаем 1024 байта от пира
        recv_string_message = str(recv_message.decode('utf-8'))  # переводим сообщение в строку
        if recv_string_message.find(':') != -1:
            mess = recv_string_message.split(':')
            if mess[1].find('result') != -1:
                message = mess[1].split(' ')
                if mess[1].find('OK') != -1:
                    for i in list_admin_chats:
                        if i.port == int(mess[2]) and i.name == message[0]:
                            i.is_blocked = 0
                else:
                    for i in list_admin_chats:
                        if i.port == int(mess[2]) and i.name == message[0]:
                            i.is_blocked = 1
            else:
                mark = False
                for i in list_admin_chats:
                    print(i.name)
                    if i.port == int(mess[2]) and i.is_blocked == 0 and i.name == mess[0]:
                        mark = True

                if mark is True:
                    message = mess[0] + ': ' + mess[1]
                    print('\r%s\n' % message, end='')  # выводим в консоль сообщение от пира

        elif recv_string_message.find('/') != -1:
            mess = recv_string_message.split('/')
            if mess[1] == 'You are admin':
                person = group_chat(mess[0], int(mess[2]), 0, 1)
                list_admin_chats.append(person)
                print(mess[1])
            elif mess[1] == 'i want to join':
                person = group_chat(mess[0], int(mess[2]), 1, 0)
                list_admin_chats.append(person)
                if name != mess[0]:
                    for i in list_admin_chats:
                        if i.port == int(mess[2]) and i.is_admin == 1 and name == i.name:
                            message = mess[0] + ' want to join!'
                            message = message + '\nEnter his login and your solution with the word "result" (example "Ivan result OK"): '
                            print(message)


# функция, отвечающая за отправку сообщений всем пирам
def SendBroadcastMessageForChat():
    global name
    global sendSocket
    global port
    sendSocket.setblocking(False)  # не блокируем сокет, с которого происходит отправка широковещательных сообщений
    while True:  # бесконечный цикл
        data = input()
        if data == 'Выход()':
            close_message = '!@#' + name  # формируем сообщение, регламентирующее закрытие
            sendSocket.sendto(close_message.encode('utf-8'),
                              ('255.255.255.255', port))  # отправляем сообщение всем пирам в подсети
            os._exit(1)  # выходим из программы
        elif data != '' and data != 'Выход()':
            send_message = name + ':' + data + ':' + str(port)
            sendSocket.sendto(send_message.encode('utf-8'),
                              ('255.255.255.255', port))
        else:
            print('Напишите сначала сообщение!')


def SendBroadcastOnlineStatus():
    global name
    global sendSocket
    global port
    sendSocket.setblocking(False)  # не блокируем сокет, с которого происходит отправка широковещательных соообщений
    while True:
        time.sleep(1)
        sendSocket.sendto(name.encode('utf-8'), ('255.255.255.255', port))  # отправка имени пира, пока он в сети


# главная функция
def main():
    global list_admin_chats

    global broadcastSocket
    # сокет для реализации получения сообщений от пиров
    broadcastSocket = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM)  # инициализация сокета для работы с IPv4-адресами, используя
    # протокол UDP
    broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                               1)  # присваиваем параметр SO_REUSEADDR на уровне библиотеки, SO_REUSEADDR - указывает
    # на то, что сразу несколько приложений могут слушать сокет
    broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,
                               1)  # присваиваем параметр SO_BROADCAST на уровне библиотеки, SO_BROADCAST - указывает
    # на то, что пакеты будут широковещательные
    # broadcastSocket.bind(('0.0.0.0', 8080))  # биндимся к адресу '0.0.0.0', чтобы прослушивать все интерфейсы
    global sendSocket
    # сокет для реализации отправки сообщений пирам
    sendSocket = socket.socket(socket.AF_INET,
                               socket.SOCK_DGRAM)  # инициализация сокета для работы с IPv4-адресами, используя
    # протокол UDP
    sendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,
                          1)  # присваиваем параметр SO_BROADCAST на уровне библиотеки, SO_BROADCAST - указывает на
    # то, что пакеты будут широковещательные

    print('*************************************************')
    print('*  Добро пожаловать в наш групповой-чат!        *')
    print('*  Чтобы выйти, отправьте сообщение: Выход()    *')

    print('*************************************************')

    global name
    name = ''
    while True:
        if not name:
            name = input('Ваше имя: ')
            if not name:
                print('Введите непустое имя!')
            else:
                break

    print('Choose option')
    print('1. Create chat')
    print('2. Join chat')
    while True:
        option = int(input())
        if option == 1:
            global port
            port = int(input('Введите порт'))
            broadcastSocket.bind(('0.0.0.0', port))
            admin = name + '/' + 'You are admin' + '/' + str(port)
            sendSocket.sendto(admin.encode('utf-8'), ('255.255.255.255', port))
            sendSocket.setblocking(True)
            break
        elif option == 2:
            port = int(input('Введите порт'))
            broadcastSocket.bind(('0.0.0.0', port))
            mess = name + '/' + 'i want to join' + '/' + str(port)
            sendSocket.sendto(mess.encode('utf-8'), ('255.255.255.255', port))
            break
        else:
            print('make correct choice')

    print('*************************************************')

    global recvThread
    recvThread = Thread(target=GetUdpChatMessage)  # поток для получения сообщений от пиров

    global sendMsgThread
    sendMsgThread = Thread(target=SendBroadcastMessageForChat)  # поток для отправки сообщений от пиров

    global current_online
    current_online = []  # список имя пиров, которые находятся в сети

    global sendOnlineThread
    sendOnlineThread = Thread(target=SendBroadcastOnlineStatus)  # поток для отправки статусов, что пир в сети

    recvThread.start()  # запуск потока для получения сообщений от пиров
    sendMsgThread.start()  # запуск потока для отправки сообщений всем пирам
    sendOnlineThread.start()  # запуск поток для отправки статусов, что пир в сети

    recvThread.join()  # блокируем поток, в котором осуществляется вызов до тех пор, пока recvThread не будет завершён
    sendMsgThread.join()  # блокируем поток, в котором осуществляется вызов до тех пор, пока sendMsgThread не будет завершён
    sendOnlineThread.join()  # блокируем поток, в котором осуществляется вызов до тех пор, пока sendOnlineThread не будет завершён


if __name__ == '__main__':
    main()