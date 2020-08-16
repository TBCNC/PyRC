'''
Messages will be formatted in the following way:
-First 8 bits will represent message type
-Rest of the message will contain data
'''
import enum
import pickle
#All types of messages
class MessageType(enum.Enum):
    ServerMessage=1
    UserMessage=2
    ServerWelcome=3
    UserInfo=4
    UserInfoResp=5
    GetUserListReq=6
    GetUserListResp=7
    NewUserJoined=8
    UserDisconnected=9
    WhisperMessage=10
    WhisperMessageError=11
#Very basic setup, add things later here such as channel, date, etc.
class Message:
    def __init__(self,msgtype,msg):
        self.msgtype=msgtype
        self.msg=msg