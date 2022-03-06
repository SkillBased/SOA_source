#!/usr/bin/python3

import socket
import threading
import pyaudio

import time
import struct

from config import ServerMessage, SOUND_THRESHOLD

def validate_sounds(sound_bytes):
    cnt = len(sound_bytes) / 2
    format_ = "%dh"%(cnt)
    upckd = struct.unpack(format_, sound_bytes)
    ms = 0
    for x in upckd:
        ms += x * x
    rms = ms ** 0.5
    return rms > SOUND_THRESHOLD

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.live = [0, time.time()]
        self.hotline = [-1, -1]
        self.username = "anonymous"
        command_thread = threading.Thread(target=self.exec_input).start()

    def exec_input(self):
        inp = "pass"
        self.username = input("Enter your username: ")
        print("use connect/disconnect commands to manage connections")
        while (inp != "exit"):
            if (inp == "connect"):
                self.connect(input("Host: "), int(input("Port: ")))
            if (inp == "move"):
                target = input("Which room to move to: ")
                request = ServerMessage()
                request.add("user", self.username)
                request.add("move", target)
                request.send_to(self.sock)
            elif (inp == "disconnect" and self.hotline != [-1, -1]):
                request = ServerMessage()
                request.add("user", self.username)
                request.add("disconnect", "request")
                request.send_to(self.sock)
            inp = input("~# ")
        print("exiting system")

    def connect(self, ip, port):        
        while 1:
            try:
                self.sock.connect((ip, port))
                break
            except Exception as e:
                print(f"Couldn't connect to server: {e}")
                time.sleep(0.125)
        
        handshake = ServerMessage()
        handshake.add("user", self.username)
        handshake.add("room", "general")
        handshake.send_to(self.sock)

        chunk_size = 1024
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000

        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True, frames_per_buffer=chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk_size)
        
        print("Connected to Server")

        self.hotline[0] = threading.Thread(target=self.receive_server_data)
        self.hotline[0].start()
        self.hotline[1] = threading.Thread(target=self.send_data_to_server)
        self.hotline[1].start()

    def receive_server_data(self):
        while True:
            try:
                message = ServerMessage().load_from(self.sock)
                if (message.data.get("disconnect") == "OK"):
                    self.sock.close()
                    break
                if (message.data.get("members") is not None):
                    print(f"members in your channel: {message.data['members']}")
                if (message.data.get("audio-size") is not None):
                    print(f"playing sounds of user {message.data['user']}")
                    self.playing_stream.write(message.audio)
            except Exception as e:
                print(e)

    def send_data_to_server(self):
        while True:
            try:
                snd_data = self.recording_stream.read(1024)
                message = ServerMessage()
                message.add("user", self.username)
                if (validate_sounds(snd_data)):
                    self.live = [0.5, time.time()]
                    message.add("audio-size", len(snd_data))
                    message.audio = snd_data
                else:
                    self.live = [max(0, self.live[0] - (time.time() - self.live[1])), time.time()]
                    if (self.live[0] > 0):
                        message.add("audio-size", len(snd_data))
                        message.audio = snd_data
                
                message.send_to(self.sock)
            except Exception as e:
                break

client = Client()