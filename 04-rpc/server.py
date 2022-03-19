import grpc
import transport_pb2
import transport_pb2_grpc
from concurrent import futures

import random

class GameServer:
    def __init__(self):
        self._free_user_id = 0
        self._users_online = {}

        self._game_status = 0
        self._message_id = 0
        self._chat = {}
    
    def accept_user(self, name, address):
        uid = self._free_user_id
        self._free_user_id += 1
        self._users_online[uid] = {"name": name, "ip": address, "role": 0, "status": 0}
        if (self._free_user_id > 4):
            self.init_game()
        return uid
    
    def exec_command(self, command):
        split_cmd = command.split()
        if (command[0] == "kill"):
            username = command[1]
            for uid in self._users_online.keys():
                if (self._users_online[uid]["name"] == username):
                    self._users_online[uid]["status"] = 1
    
    def init_game(self):
        uids = self._users_online.keys()
        mafs = [random.choice(uids) for i in range(len(uids) / 5)]
        for uid in uids:
            self._users_online[uid]["status"] = 1
            if (uid in mafs):
                self._users_online[uid]["role"] = 1
            else:
                self._users_online[uid]["role"] = 0
    
    def send_update(self, uid, latest_message):
        print("creating upd message")
        player_ids = []
        player_names = []
        player_status = []
        new_messages = []
        for uid in self._users_online.keys():
            player_ids.append(uid)
            player_names.append(self._users_online[uid]["name"])
            player_status.append(self._users_online[uid]["status"])
        for message_id in range(latest_message + 1, self._message_id):
            new_messages.append((message_id, self._chat[message_id]))
        print(player_names)
        update = transport_pb2.Update(status = self._game_status,
                                      playerids = player_ids, 
                                      playernames = player_names,
                                      playerstat = player_status,
                                      messages = new_messages)
        print(update)
        return update


main_server = GameServer()

class ConnectionServiceServicer(transport_pb2_grpc.ConnectionServiceServicer):
    def accept(self, request, context):
        print("connection requested")
        useraddr = request.connip
        username = request.name
        user_id = main_server.accept_user(username, useraddr)
        print(f"{username} connected from {useraddr} --- user id: {user_id}")
        return transport_pb2.ServerAck(userid=user_id, ack=True)

class UpdateServiceServicer(transport_pb2_grpc.UpdateServiceServicer):
    def process(self, request, context):
        print("update requested", flush=True)
        uid = request.userid
        latest_message = request.last_message
        return main_server.send_update(uid, latest_message)        

class ActionServiceServicer(transport_pb2_grpc.ActionServiceServicer):
    def process(self, request, context):
        command = request.action
        main_server.exec_command(command)
        return transport_pb2.ServerAck(userid=user_id, ack=True)

def startup():
    print("initiating server")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    transport_pb2_grpc.add_ConnectionServiceServicer_to_server(ConnectionServiceServicer(), server)
    transport_pb2_grpc.add_UpdateServiceServicer_to_server(UpdateServiceServicer(), server)
    transport_pb2_grpc.add_ActionServiceServicer_to_server(ActionServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.add_insecure_port("[::]:50052")
    server.add_insecure_port("[::]:50053")
    server.start()
    print("server is up")
    server.wait_for_termination()

startup()
