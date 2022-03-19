import grpc
import transport_pb2
import transport_pb2_grpc

import socket
import threading
import time

class GameClient:
    def __init__(self, connect_tries=3):
        self._ipaddr = socket.gethostbyname(socket.gethostname())
        self._username = input("Enter your name/nickname: ")
        self._user_id = -1
        self._channel = grpc.insecure_channel('localhost:50051', options=(('grpc.enable_http_proxy', 0),))
        conn_latest_error = None
        while (self._user_id == -1 and connect_tries > 0):
            stub = transport_pb2_grpc.ConnectionServiceStub(self._channel)
            userdata = transport_pb2.Connection(connip=self._ipaddr, name=self._username)
            print("requesting connection, waiting for 20 seconds until retry")
            try:
                response = stub.accept(userdata)
                if (response.ack):
                    self._user_id = response.userid
                    print(f"connected, user id: {self._user_id}")
                else:
                    self._user_id = -2
                    print("connection refused")
                    break
            except Exception as e:
                conn_latest_error = e
            connect_tries -= 1
        if (self._user_id == -1):
            print(f"connection failed, last error: {conn_latest_error}")
        else:
            self._game_status = 0
            self._player_data = {}
            self._chat = {}
            self._last_message = 0
    
    def start(self):
        update_thread = threading.Thread(target=self.run).start()
        command_thread = threading.Thread(target=self.command_line).start()
    
    def run(self):
        self._upd_channel = grpc.insecure_channel('localhost:50052', options=(('grpc.enable_http_proxy', 0),))
        upd_stub = transport_pb2_grpc.UpdateServiceStub(self._upd_channel)
        print("upd thread started")
        while True:
            print("requesting update")
            try:
                upd_request = transport_pb2.Lookup(userid=self._user_id, last_message=self._last_message)
                upd_msg = upd_stub.process(upd_request)
                print("got update")
                pids, pnames, pstat = upd_msg.playerids, upd_msg.playernames, upd_msg.playerstat
                self._game_status = upd_msg.status
                self._player_data = {}
                chat = upd_msg.messages
                for i in range(len(pids)):
                    pid, name, status = pids[i], pnames[i], pstat[i]
                    self._player_data[pid] = {"name": name, "status": status}
                for msg_id, msg_text in chat:
                    if (msg_id > self._last_message):
                        self._last_message = msg_id
                    print(msg_text)
            except Exception as e:
                continue
    
    def command_line(self):
        self._cmd_channel = grpc.insecure_channel('localhost:50053', options=(('grpc.enable_http_proxy', 0),))
        cmd_stub = transport_pb2_grpc.ActionServiceStub(self._cmd_channel)
        command = input()
        while (command != "/exit"):
            if (command == "/status"):
                if (self._game_status == 0):
                    print("game offline")
                else:
                    print("game online,", "day" if self._game_status == 1 else "night")
                for pid in self._player_data.keys():
                    player = self._player_data[pid]
                    stat_text = "alive" if player["status"] > 1 else "dead"
                    print(f"{player['name']} is {stat_text}")
            
            if (command[:5] == "/kill"):
                action = transport_pb2.Action(userid = self._user_id, action = command[1:])
                ack = cmd_stub.commit(action)
            
            command = input()


if __name__ == "__main__":
    print("starting client")
    client = GameClient()
    if (client._user_id != -1):
        client.start()