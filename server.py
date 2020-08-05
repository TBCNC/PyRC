import socket
import threading
from user import User

#Acts as a simple struct for handling connections
class Connection:
    def __init__(self,conn_sock,user_data):
        self.conn_sock=conn_sock
        self.user_data=user_data

class Server:
    #We will need to make a mutex/semaphore for this perhaps and many other things to prevent race conditions
    client_list=[]
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
                #self.client_list.append(cliSock)#Socket for now, will update to have a user object
                welcomeMsg = "You have joined "+self.name+",welcome.\nMOTD:"+self.motd
                cliSock.send(welcomeMsg.encode("utf8"))#Maybe change this to unicode
                testUser = User("Hayden","Woop","#FFFFFF")#Test user for testing the user data structure, update when able to query for user
                newConn=Connection(cliSock,testUser)
                handle_client_thread=threading.Thread(target=self.handle_client,args=(newConn,))
                handle_client_thread.start()
                self.client_list.append(newConn)
                self.running_threads.append(handle_client_thread)
            except BlockingIOError:
                continue
    def handle_client(self,conn):
        while self.server_running:
            try:
                data=conn.conn_sock.recv(self.buffer_size)
                if not data:
                    print(conn.user_data.username+" has disconnected.")
                    self.client_list.remove(conn)
                    break
                msgToSend=conn.user_data.username+":"+data.decode("utf8")
                print(msgToSend)
                self.send_to_all(msgToSend,conn)
            except BlockingIOError:
                continue
    #Send a message to all connected sockets other than exclusion_sock
    def send_to_all(self,msg,exclusion_conn=None):
        for conn in self.client_list:
            if conn!=exclusion_conn:
                conn.conn_sock.send(msg.encode("utf8"))
    def close_all_sockets(self):
        for conn in self.client_list:
            conn.conn_sock.close()
    def join_all_threads(self):
        for thread in self.running_threads:
            thread.join()
    def close_server(self):
        self.server_running=False
        self.join_all_threads()
        self.close_all_sockets()
        self.sock.shutdown(socket.SHUT_RDWR)#Stop receive and sends
        self.sock.close()

ourServer = Server("127.0.0.1",1246,"Charles' Server","Welcome to my server")
try:
    ourServer.start_server()
except KeyboardInterrupt:
    print("Closing server...")
    ourServer.close_server()
    print("Server closed.")
