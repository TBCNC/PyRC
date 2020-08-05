import socket
import threading
from user import User

class Client:
    running_threads=[]
    def __init__(self,user,addr,port):
        self.user = user
        self.addr = addr
        self.port = port
        self.client_on=True
        self.buffer_size=1024
    def connect_to_server(self):
        print("Connecting to server...")
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((self.addr,self.port))
        self.sock.setblocking(False)
        print("Connected to server!")
        handle_messages_thread = threading.Thread(target=self.handle_messages,args=())
        handle_messages_thread.start()
        self.running_threads.append(handle_messages_thread)
        while self.client_on:
            msgToSend=input()
            if msgToSend=="/quit":
                self.client_on=False
                break
            self.send_message(msgToSend)
    def handle_input(self,inp):
        if inp=="/quit":
            self.client_on=False
        else:
            self.send_message(inp)
    def handle_messages(self):
        while self.client_on:
            try:
                data=self.sock.recv(self.buffer_size)
                if not data:
                    print("Lost connection with server..")
                    self.client_on=False
                    break
                print(data.decode("utf8"))
            except BlockingIOError:
                continue
    #Maybe should do better error handling here? Fine for now
    def send_message(self,msg):
        self.sock.send(msg.encode("utf8"))
    def join_threads(self):
        for thread in self.running_threads:
            thread.join()
    def close_client(self):
        self.join_threads()
        self.sock.close()

ourUser = User("Charles","Test Bio")
ourClient = Client(ourUser,"127.0.0.1",1246)
try:
    ourClient.connect_to_server()
    ourClient.close_client()
except ConnectionRefusedError:
    print("Could not connect to server..")
print("Closed connection with server.")