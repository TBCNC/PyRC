A multi-threaded chat application written in Python3 and designed with Qt Designer
# Starting the server
You can start the server with the following commands:
```
python3 server.py server.py -i <ip_address> -p <port> -n <name> -m <motd>
```
or
```
python3 server.py server.py --ip=<ip_address> --port=<port> --name=<name> --motd=<motd>
```
1
To find out more about what these options mean, you can see the help page with:
```
python3 server.py -h
```
# Using the client
To launch the client, simply type in your terminal:
```
python3 main.py
```
Fill in the form you are presented with in order to connect to a server.
The fields bio and colour are optional personal features.