import socket
import threading
import pickle
from user import User
from messages import Message
from messages import MessageType

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
                ourMessage=pickle.loads(data)
                self.handle_message(ourMessage)
            except BlockingIOError:
                continue
    def handle_message(self,msg):
        if msg.msgtype==MessageType.UserMessage or msg.msgtype==MessageType.ServerWelcome:#Add different colour coding later
            print(msg.msg)
        elif msg.msgtype==MessageType.ServerGetUserInfo:
            print("GOT USER REQ")
            userData = pickle.dumps(self.user)
            ourMsg = Message(MessageType.UserInfo,userData)
            data=pickle.dumps(ourMsg)
            self.sock.send(data)#Bodged for now
            print("SENT USER RES")
    
    #Maybe should do better error handling here? Fine for now
    def send_message(self,msg):
        newMsg = Message(MessageType.UserMessage,msg)
        toSend = pickle.dumps(newMsg)
        self.sock.send(toSend)
    def join_threads(self):
        for thread in self.running_threads:
            thread.join()
    def close_client(self):
        self.join_threads()
        self.sock.close()

ourUser = User("Charles","Test Bio")
ourClient = Client(ourUser,"127.0.0.1",1254)
try:
    ourClient.connect_to_server()
    ourClient.close_client()
except ConnectionRefusedError:
    print("Could not connect to server..")
print("Closed connection with server.")