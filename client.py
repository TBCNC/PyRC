import socket
import threading
import pickle
from user import User
from messages import Message
from messages import MessageType
from PyQt5 import QtCore, QtGui, QtWidgets

class Client:
    running_threads=[]
    def __init__(self,user,addr,port,qtwin_login=None):
        self.user = user
        self.addr = addr
        self.port = port
        self.client_on=True
        self.buffer_size=1024
        self.qtwin_login=qtwin_login
    
    def connect_to_server(self):
        try:
            print("Connecting to server...")
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sock.connect((self.addr,self.port))
            self.sock.setblocking(False)
            print("Connected to server!")
            handle_messages_thread = threading.Thread(target=self.handle_messages,args=())
            handle_messages_thread.start()
            self.running_threads.append(handle_messages_thread)
            return (True,"OK") # Indicate successful connection to client
        except Exception as err:
            return (False,"An error has occurred while connecting:{}".format(str(err)))
    def send_user_info(self,user):
        userdata = pickle.dumps(user)
        messageobj = Message(MessageType.UserInfo,userdata)
        self.sock.send(pickle.dumps(messageobj))
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
        elif msg.msgtype==MessageType.UserInfoResp:
            if msg.msg=="OK":
                print("Joined server successfully.")
                self.qtwin_login.updateStatusLabel("Status:Joined server successfully.")
            else:
                print("Rejected from server:{}".format(msg.msg))
                self.qtwin_login.errBox("Connection Error","Rejected from server:{}".format(msg.msg))
                self.qtwin_login.enableButton(True)
                self.qtwin_login.updateStatusLabel("Status:Waiting for input...")
    
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
'''Old terminal UI
#Lack of input validation, proof of concept, will use gui
print("Welcome to PyRC")
ipaddr = input("Please enter an IP address:")
port = int(input("Please enter the port number:"))
name=input("Please input your username:")
bio=input("Input a bio (optional):")
ourUser = User(name,bio)
ourClient = Client(ourUser,ipaddr,port)
try:
    ourClient.connect_to_server()
    ourClient.close_client()
except ConnectionRefusedError:
    print("Could not connect to server..")
'''