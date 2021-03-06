import socket
import time
import pickle
import threading
from messages import Message
from messages import MessageType
from user import User
import sys,getopt
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
        ourMsg = Message(MessageType.ServerWelcome,"You have joined " + self.name + ",welcome.\nMOTD:"+self.motd)
        data = pickle.dumps(ourMsg)
        conn.send(data)
    def send_new_user_joined(self,user,exconn=None):
        ourMsg=Message(MessageType.NewUserJoined,user)
        self.send_msg_to_all(ourMsg,exconn)
    def find_user(self,username):
        for key,val in self.client_list.items():
            if val.user_data.username==username:
                return key
        return None
    def send_message(self,msgtype,msg,conn):
        ourMessage=Message(msgtype,msg)
        data=pickle.dumps(ourMessage)
        conn.send(data)
    def handle_client(self,conn):
        while self.server_running:
            try:
                data=conn.recv(self.buffer_size)
                if not data:
                    username=self.client_list[conn].user_data.username
                    print(username+" has disconnected.")
                    self.client_list.pop(conn)
                    self.send_msg_to_all(Message(MessageType.UserDisconnected,username))
                    break
                fullMsg = pickle.loads(data)
                self.handle_message(fullMsg,conn)
            except BlockingIOError:
                continue
            except OSError:#Socket has been closed by server
                break
    
    def handle_message(self,msg,src):
        if msg.msgtype==MessageType.UserMessage:#Add different colour coding later
            print(msg.msg)
            msgtosend = Message(MessageType.UserMessage,msg.msg)
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
        elif msg.msgtype==MessageType.WhisperMessage:
            #Separate user and rest of message with a space
            contents=msg.msg.split(" ",1)
            print("Received whisper:{}".format(contents))
            conntosend=self.find_user(contents[0])
            if conntosend!=None:
                print("Sending whisper")
                #Found a user to send to
                self.send_message(MessageType.UserMessage,contents[1],conntosend)
            else:
                self.send_message(MessageType.WhisperMessageError,"User {} does not exist.".format(contents[0]),src)
            
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

def print_help():
    print("PyRC Server Setup")
    print("Command usage:\nserver.py -i <ip_address> -p <port> -n <name> -m <motd>")
    print("or\nserver.py --ip=<ip_address> --port=<port> --name=<name> --motd=<motd>")
    print("Properties and what they mean:")
    print("--ip - The IP address you wish to bind to")
    print("--port - The port you wish for the server to run on")
    print("--name - The name of your server")
    print("--motd - A MOTD that users will see when joining your server (optional)")
def main(argv):
    ipaddr=None
    port=None
    name=None
    motd=""
    try:
        opts,args=getopt.getopt(argv,"hi:p:n:m:",["ip=","port=","name=","motd="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt,arg in opts:
        if opt=='-h':
            print_help()
            sys.exit()
        elif opt in ("-i","--ip"):
            ipaddr=arg
        elif opt in ("-p","--port"):
            port=arg
        elif opt in ("-n","--name"):
            name=arg
        elif opt in ("-m","--motd"):
            motd=arg
    if ipaddr==None:
        print("Missing IP address.")
        sys.exit(2)
    if port==None:
        print("Missing port number.")
        sys.exit(2)
    if not port.isnumeric():
        print("Port number not numeric.")
        sys.exit(2)
    if name==None:
        print("Missing name.")
        sys.exit(2)
    print("PyRC Chat Server")
    print("Properties:")
    print("IP:{}:{}".format(ipaddr,port))
    print("Name:"+name)
    print("MOTD:{}".format(motd if motd!="" else "None"))
    print("Initializing server...")
    ourServer=Server(ipaddr,int(port),name,motd)
    print("Starting server...")
    try:
        ourServer.start_server()
        print("Server started.")
    except KeyboardInterrupt:
        print("Closing server...")
        ourServer.close_server()
        print("Server closed.")
if __name__=="__main__":
    main(sys.argv[1:])