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
    running_threads={}#Dictionary with socket as key, thread as value
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
                handle_client_thread=threading.Thread(target=self.handle_client,args=(cliSock,))
                handle_client_thread.start()
                self.running_threads[cliSock]=handle_client_thread
            except BlockingIOError:
                continue
    #Used to check if username already exists to grant/deny entry into the server (could reduce to list comprehension?)
    def get_all_users(self):
        returnlist=[]
        for key,value in self.client_list.items():
            returnlist.append(value.user_data.username)
        return returnlist
    def send_all_users(self,conn):
        msg = Message(MessageType.GetUserListResp,pickle.dumps(self.get_all_users()))
        data=pickle.dumps(msg)
        conn.send(data)
    def username_exists(self,name):
        for key,val in self.client_list.items():
            if val.user_data.username==name:
                return True
        return False
    def send_welcome_msg(self,conn):
        ourMsg = Message(MessageType.ServerWelcome,"You have joined " + self.name + ",welcome.\nMOTD:"+self.motd+"\n")
        data = pickle.dumps(ourMsg)
        conn.send(data)
    def send_new_user_joined(self,user,exconn=None):
        ourMsg=Message(MessageType.NewUserJoined,user)
        self.send_msg_to_all(ourMsg,exconn)
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
            except OSError:#Socket has been closed by server
                break
    
    def handle_message(self,msg,src):
        if msg.msgtype==MessageType.UserMessage:#Add different colour coding later
            strtosend = "<"+self.client_list[src].user_data.username+">:"+msg.msg
            print(strtosend)
            msgtosend = Message(MessageType.UserMessage,strtosend)
            self.send_msg_to_all(msgtosend,src)
        elif msg.msgtype==MessageType.UserInfo:
            userData = pickle.loads(msg.msg)
            if not self.username_exists(userData.username):
                #Grant access to server
                newconn=Connection(src,userData)
                self.client_list[src]=newconn
                print("Accepted user " + userData.username + " into server list.")
                self.send_message(MessageType.UserInfoResp,"OK",src)
                time.sleep(0.1)
                self.send_welcome_msg(src)
                time.sleep(0.1)
                self.send_new_user_joined(userData.username,src)#Maybe change this to user object later
            else:
                print("Username already taken")
                self.send_message(MessageType.UserInfoResp,"Username already taken.",src)
                self.disconnect_client(src)
        elif msg.msgtype==MessageType.GetUserListReq:
            print("All users requested")
            self.send_all_users(src)
        
    #Send a message to all connected sockets other than exclusion_sock
    def send_msg_to_all(self,msg,exclusion_conn=None):
        for conn in self.client_list:
            if conn!=exclusion_conn:
                conn.send(pickle.dumps(msg))
    #Drops a client and running threads of that client
    def disconnect_client(self,sock):
        print("Disconnecting client")
        sock.close()
        if sock in self.running_threads:
            self.running_threads.pop(sock)
        if sock in self.client_list:#If they were given a conn object (i.e accepted into the server fully)
            self.client_list.pop(sock)
        print("Disconnected client")
    def close_all_sockets(self):
        for conn in self.client_list:
            conn.close()
    def join_all_threads(self):
        for key,thread in self.running_threads.items():
            thread.join()
    def close_server(self):
        self.server_running=False
        self.join_all_threads()
        self.close_all_sockets()
        self.sock.shutdown(socket.SHUT_RDWR)#Stop receive and sends
        self.sock.close()

print("Welcome to PyRC server")
ipaddr = input("Please enter the IP you are binding to:")
port = int(input("Please enter a port:"))
servername = input("Enter a server name:")
motd = input("Enter a MOTD:")
ourServer = Server(ipaddr,port,servername,motd)
try:
    ourServer.start_server()
except KeyboardInterrupt:
    print("Closing server...")
    ourServer.close_server()
    print("Server closed.")
