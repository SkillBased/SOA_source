#!/usr/bin/python3

import socket
import threading
import struct
import time

from config import ServerMessage

class Server:
    def __init__(self):
            self.ip = socket.gethostbyname(socket.gethostname())
            while 1:
                try:
                    self.port = int(input('Enter port number to run on --> '))

                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.bind((self.ip, self.port))

                    break
                except Exception as e:
                    print(f"Couldn't bind to that port: {e}")
                    time.sleep(0.125)

            self.rooms = {"general": [], "small-talk": [], "void": []}
            self.users = {}

            self.connections = []
            self.accept_connections()

    def accept_connections(self):
        self.sock.listen(100)
    
        print('Running on IP: '+self.ip)
        print('Running on port: '+str(self.port))
        
        while True:
            c, addr = self.sock.accept()
            print(f"accepted connection from {addr}")
    
            handshake = ServerMessage().load_from(c)
            self.users[handshake.data["user"]] = handshake.data["room"]
            if (self.rooms[handshake.data["room"]] is not None):
                self.rooms[handshake.data["room"]].append((handshake.data["user"], c))
            else:
                self.users[handshake.data["user"]] = "general"
                self.rooms["general"].append((handshake.data["user"], c))
            
            self.stat_for(handshake.data["user"], c)

            print(f'{handshake.data["user"]} joined in {handshake.data["room"]}')
            print(self.rooms)

            threading.Thread(target=self.handle_client,args=(c,addr,)).start()
    
    def stat_for(self, username, sock):
        user_room = self.users[username]
        members = ""
        for udata in self.rooms[user_room]:
            name = udata[0]
            members = members + name + ", " 
        response = ServerMessage()
        response.add("members", members[:-2])
        response.send_to(sock)
        
    def broadcast(self, sock, message):
        user_room = self.users[message.data["user"]]
        for client in self.rooms[user_room]:
            target = client[1]
            # if target == sock: continue
            try:
                message.send_to(target)
            except Exception as e:
                print(f"Couldn't deliver message to {client[0]} @ {client[1]}: {e}")
                pass

    def handle_client(self, c, addr):
        while 1:
            try:
                message = ServerMessage().load_from(c)
                if (message.data.get("disconnect") is not None):
                    user = message.data["user"]
                    room = self.users[user]
                    idx = -1
                    for i in range(len(self.rooms[room])):
                        if (self.rooms[room][i][0] == user):
                            idx = i
                            break
                    self.rooms[room].pop(idx)
                    self.users.pop(user)
                    print(f"{user} left")
                    ack = ServerMessage()
                    ack.add("disconnect", "OK")
                    ack.send_to(c)
                    c.close()
                    for udata in self.rooms[room]:
                        self.stat_for(udata[0], udata[1])
                    break
                if (message.data.get("move")is not None):
                    user = message.data["user"]
                    room = message.data["move"]
                    if (room in self.rooms.keys()):
                        idx = -1
                        for i in range(len(self.rooms[self.users[user]])):
                            if (self.rooms[self.users[user]][i][0] == user):
                                idx = i
                                break
                        udata = self.rooms[self.users[user]][idx]
                        self.rooms[self.users[user]].pop(idx)
                        self.users[user] = room
                        self.rooms[room].append(udata)
                        print(f"{user} moved to {room}")
                    for udata in self.rooms[room]:
                        self.stat_for(udata[0], udata[1])
                self.broadcast(c, message)
            except socket.error:
                c.close()

server = Server()