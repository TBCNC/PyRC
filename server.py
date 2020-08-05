import socket
import time
import pickle
import threading
from messages import Message
from messages import MessageType
from user import User

#Acts as a simple struct for handling connections
class Connection:
    def __init__(self,conn_sock,user_data):
        self.conn_sock=conn_sock
        self.user_data=user_data

class Server:
    #We will need to make a mutex/semaphore for this perhaps and many other things to prevent race conditions
    client_list={}#Dictionary with socket as key, Connection object as value
    running_threads=[]
    def __init__(self,addr,port,name,motd):
        self.addr=addr
        self.port=port
        self.name=name
        self.motd=motd
        self.buffer_size=1024
    def start_server(self):
        print("Starting server...")
        self.server_running=True
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind((self.addr,self.port))
        self.sock.listen()
        print("Started server!")
        while self.server_running:
            try:
                cliSock,addr=self.sock.accept()
                cliSock.setblocking(False)
                print("Client connected from %s" % str(addr))
                self.send_welcome_msg(cliSock)
                time.sleep(0.5)
                self.send_user_req(cliSock)
                testUser = User("Hayden","Woop","#FFFFFF")#Test user for testing the user data structure, update when able to query for user
                handle_client_thread=threading.Thread(target=self.handle_client,args=(cliSock,))
                handle_client_thread.start()
                self.running_threads.append(handle_client_thread)
            except BlockingIOError:
                continue
    def send_welcome_msg(self,conn):
        ourMsg = Message(MessageType.ServerWelcome,"You have joined " + self.name + ",welcome.\nMOTD:"+self.motd)
        data = pickle.dumps(ourMsg)
        conn.send(data)
    def send_user_req(self,conn):
        ourMsg = Message(MessageType.ServerGetUserInfo,"")
        data=pickle.dumps(ourMsg)
        conn.send(data)
        print("SENT USER REQ")
    def send_message(self,msgtype,msg,conn):
        ourMessage=Message(msgtype,msg)
        data=pickle.dumps(ourMessage)
        conn.send(data)
    def handle_client(self,conn):
        while self.server_running:
            try:
                data=conn.recv(self.buffer_size)
                if not data:
                    print(self.client_list[conn].user_data.username+" has disconnected.")
                    self.client_list.pop(conn)
                    break
                fullMsg = pickle.loads(data)
                self.handle_message(fullMsg,conn)
            except BlockingIOError:
                continue
    def handle_message(self,msg,src):
        if msg.msgtype==MessageType.UserMessage:#Add different colour coding later
            strtosend = self.client_list[src].user_data.username+":"+msg.msg
            print(strtosend)
            msgtosend = Message(MessageType.UserMessage,strtosend)
            self.send_msg_to_all(msgtosend,src)
        elif msg.msgtype==MessageType.UserInfo:
            userData=pickle.loads(msg.msg)
            print("RECIEVED USER " + userData.username)
            ourUser = User(userData.username,userData.bio,userData.colour)
            ourConn = Connection(src,ourUser)
            self.client_list[src]=ourConn
    #Send a message to all connected sockets other than exclusion_sock
    def send_msg_to_all(self,msg,exclusion_conn=None):
        for conn in self.client_list:
            if conn!=exclusion_conn:
                conn.send(pickle.dumps(msg))
    def close_all_sockets(self):
        for conn in self.client_list:
            conn.close()
    def join_all_threads(self):
        for thread in self.running_threads:
            thread.join()
    def close_server(self):
        self.server_running=False
        self.join_all_threads()
        self.close_all_sockets()
        self.sock.shutdown(socket.SHUT_RDWR)#Stop receive and sends
        self.sock.close()

ourServer = Server("127.0.0.1",1254,"Charles' Server","Welcome to my server")
try:
    ourServer.start_server()
except KeyboardInterrupt:
    print("Closing server...")
    ourServer.close_server()
    print("Server closed.")
