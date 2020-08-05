'''
Messages will be formatted in the following way:
-First 8 bits will represent message type
-Rest of the message will contain data
'''
import enum
#All types of messages
class MessageType(enum.Enum):
    ServerMessage=1
    UserMessage=2
    ServerGetUserInfo=3

class Message:
    def __init__(self,msgtype,msg):
        self.msgtype=msgtype
        self.msg=msg
    