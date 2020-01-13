#  !/usr/bin/env python
#  -*- conding:utf8 -*-
import socket
import select
#  创建socket文件句柄
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 999999999)
server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 999999999)
server.bind(('0.0.0.0', 8800))
server.listen(10)
server.setblocking(0)
epoll = select.epoll()
epoll.register(server.fileno(), select.EPOLLIN)

server2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server2.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 999999999)
server2.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 999999999)
server2.bind(('0.0.0.0', 8700))
server2.listen(10)
server2.setblocking(0)
epoll.register(server2.fileno(), select.EPOLLIN)

server3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server3.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server3.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 999999999)
server3.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 999999999)
server3.bind(('0.0.0.0', 8600))
server3.listen(10)
server3.setblocking(0)
epoll.register(server3.fileno(), select.EPOLLIN)

server4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server4.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 999999999)
server4.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 999999999)
server4.bind(('0.0.0.0', 8500))
server4.listen(10)
server4.setblocking(0)
epoll.register(server4.fileno(), select.EPOLLIN)

connections = {}
requests = {}
responses = {}
while True:
    events = epoll.poll()
    for fileno, event in events:
        if fileno == server.fileno():
            connection, addr = server.accept()
            connFd = connection.fileno()
            connection.setblocking(0)
            epoll.register(connFd, select.EPOLLIN)
            connections[connFd] = connection
            print('1')
        elif fileno == server2.fileno():
            connection, addr = server2.accept()
            connFd = connection.fileno()
            connection.setblocking(0)
            epoll.register(connFd, select.EPOLLIN)
            connections[connFd] = connection
            print('2')
        elif fileno == server3.fileno():
            connection, addr = server3.accept()
            connFd = connection.fileno()
            connection.setblocking(0)
            epoll.register(connFd, select.EPOLLIN)
            connections[connFd] = connection
            print('3')
        elif fileno == server4.fileno():
            connection, addr = server4.accept()
            connFd = connection.fileno()
            connection.setblocking(0)
            epoll.register(connFd, select.EPOLLIN)
            connections[connFd] = connection
            print('4')
        elif event & select.EPOLLHUP:
            print('close')
            epoll.unregister(fileno)
            connections[fileno].close()
            del connections[fileno]
        elif event & select.EPOLLIN:
            requests[fileno] = connections[fileno].recv(999999)
            epoll.modify(fileno, select.EPOLLOUT)
        elif event & select.EPOLLOUT:
            print(connections)
            for i in connections:
                if i != fileno:
                    connections[i].sendall(requests[fileno])
            epoll.modify(fileno, select.EPOLLIN)
