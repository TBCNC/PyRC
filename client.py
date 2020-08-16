import socket
import threading
import pickle
from user import User
from messages import Message
from messages import MessageType
from PyQt5 import QtCore, QtGui, QtWidgets

class Client(QtCore.QObject):
    running_threads=[]
    signal_user_accepted=QtCore.pyqtSignal()
    signal_user_denied=QtCore.pyqtSignal(str)
    signal_new_message=QtCore.pyqtSignal(str)
    signal_lost_connection=QtCore.pyqtSignal()
    signal_obtained_usernames=QtCore.pyqtSignal(list)
    signal_new_user=QtCore.pyqtSignal(str)#For now, maybe change to user
    signal_lost_user=QtCore.pyqtSignal(str)#For now, maybe change to user
    signal_whisper_error=QtCore.pyqtSignal(str)
    def __init__(self,user,addr,port):
        super(QtCore.QObject,self).__init__()
        self.user = user
        self.addr = addr
        self.port = port
        self.client_on=True
        self.buffer_size=1024
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
    def send_user_list_req(self):
        messageobj=Message(MessageType.GetUserListReq,"")
        self.sock.send(pickle.dumps(messageobj))
        print("Sent user list request")
    def handle_messages(self):
        while self.client_on:
            try:
                data=self.sock.recv(self.buffer_size)
                if not data:
                    print("Lost connection with server..")
                    self.client_on=False
                    self.signal_lost_connection.emit()
                    break
                ourMessage=pickle.loads(data)
                self.handle_message(ourMessage)
            except BlockingIOError:
                continue
    def handle_message(self,msg):
        if msg.msgtype==MessageType.UserMessage or msg.msgtype==MessageType.ServerWelcome:#Add different colour coding later
            print(msg.msg)
            self.signal_new_message.emit(msg.msg)
        elif msg.msgtype==MessageType.UserInfoResp:
            if msg.msg=="OK":
                print("Joined server successfully.")
                self.signal_user_accepted.emit()
                self.send_user_list_req()
            else:
                print("Rejected from server:{}".format(msg.msg))
                self.signal_user_denied.emit(msg.msg)
        elif msg.msgtype==MessageType.GetUserListResp:
            self.signal_obtained_usernames.emit(pickle.loads(msg.msg))
        elif msg.msgtype==MessageType.NewUserJoined:
            self.signal_new_user.emit(msg.msg)
        elif msg.msgtype==MessageType.UserDisconnected:
            self.signal_lost_user.emit(msg.msg)
        elif msg.msgtype==MessageType.WhisperMessageError:
            self.signal_whisper_error.emit(msg.msg)
    #Maybe should do better error handling here? Fine for now
    def send_message(self,msg):
        newMsg = Message(MessageType.UserMessage,msg)
        toSend = pickle.dumps(newMsg)
        self.sock.send(toSend)
    def send_whisper(self,user,msg):
        newMsg = Message(MessageType.WhisperMessage,user+" "+msg)
        toSend = pickle.dumps(newMsg)
        self.sock.send(toSend)
    def join_threads(self):
        for thread in self.running_threads:
            thread.join()
    def close_client(self):
        print("Disconnecting client")
        self.client_on=False
        self.join_threads()
        self.sock.close()
        print("Disconnected")
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