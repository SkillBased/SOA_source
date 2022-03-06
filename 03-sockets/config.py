import struct
import pickle

SOUND_THRESHOLD = 6000

class ServerMessage:
    def __init__(self):
        self.data = {}
        self.audio = bytes()
    
    def get(self, key):
        return self.data.get(key)

    def __getitem__(self, key):
        return self.data.get(key)
    
    def send_to(self, stream):
        byte_data = pickle.dumps(self.data)
        length_repr = struct.pack("l", len(byte_data))
        stream.sendall(length_repr)
        stream.sendall(byte_data)
        if (len(self.audio)):
            stream.sendall(self.audio)
    
    def load_from(self, stream):
        head = stream.recv(8)
        size = struct.unpack("l", head)[0]
        byte_data = stream.recv(size)
        self.data = pickle.loads(byte_data)
        if (self.data.get("audio-size") is not None):
            self.audio = stream.recv(self.data["audio-size"])
        return self
    
    def add(self, tag, message):
        self.data[tag] = message
