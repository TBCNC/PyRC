# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import re
from PyQt5 import QtCore, QtGui, QtWidgets
from client import Client
from user import User
import time


class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        LoginWindow.setObjectName("LoginWindow")
        LoginWindow.resize(425, 320)
        LoginWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget = QtWidgets.QWidget(LoginWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setItalic(True)
        self.label_title.setFont(font)
        self.label_title.setMouseTracking(False)
        self.label_title.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.verticalLayout.addWidget(self.label_title)
        self.label_info = QtWidgets.QLabel(self.centralwidget)
        self.label_info.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_info.setAlignment(QtCore.Qt.AlignCenter)
        self.label_info.setObjectName("label_info")
        self.verticalLayout.addWidget(self.label_info)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_serverIP = QtWidgets.QLabel(self.centralwidget)
        self.label_serverIP.setObjectName("label_serverIP")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_serverIP)
        self.text_ipaddr = QtWidgets.QLineEdit(self.centralwidget)
        self.text_ipaddr.setObjectName("text_ipaddr")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.text_ipaddr)
        self.label_port = QtWidgets.QLabel(self.centralwidget)
        self.label_port.setObjectName("label_port")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_port)
        self.text_port = QtWidgets.QLineEdit(self.centralwidget)
        self.text_port.setObjectName("text_port")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.text_port)
        self.label_username = QtWidgets.QLabel(self.centralwidget)
        self.label_username.setObjectName("label_username")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_username)
        self.text_username = QtWidgets.QLineEdit(self.centralwidget)
        self.text_username.setObjectName("text_username")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.text_username)
        self.label_bio = QtWidgets.QLabel(self.centralwidget)
        self.label_bio.setObjectName("label_bio")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_bio)
        self.text_bio = QtWidgets.QLineEdit(self.centralwidget)
        self.text_bio.setObjectName("text_bio")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.text_bio)
        self.button_connect = QtWidgets.QPushButton(self.centralwidget)
        self.button_connect.setEnabled(True)
        self.button_connect.setObjectName("button_connect")
        self.button_connect.clicked.connect(self.startConnection)
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.SpanningRole, self.button_connect)
        self.verticalLayout.addLayout(self.formLayout)
        self.label_connection_info = QtWidgets.QLabel(self.centralwidget)
        self.label_connection_info.setObjectName("label_connection_info")
        self.verticalLayout.addWidget(self.label_connection_info)
        LoginWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(LoginWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 425, 22))
        self.menubar.setObjectName("menubar")
        LoginWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(LoginWindow)
        self.statusbar.setObjectName("statusbar")
        LoginWindow.setStatusBar(self.statusbar)

        self.retranslateUi(LoginWindow)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)
    
    def validateInputs(self):
        ipregex = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        if not ipregex.match(self.text_ipaddr.text()):
            return (False,"{} is not a valid IPv4 address, try again!".format(self.text_ipaddr.text()))
        portNumber = self.text_port.text()
        if not portNumber.isnumeric():
            return (False,"{} is not an integer port number, try again!".format(portNumber))
        usernameregex = re.compile("^\w{4,12}$")
        if not usernameregex.match(self.text_username.text()):
            return (False,"Your username must be between 4 and 12 characters long with no spaces!")
        return (True,"OK")

    def errBox(self,title,msg):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle(title)
        msgbox.setText(msg)
        msgbox.setIcon(QtWidgets.QMessageBox.Critical)
        msgbox.exec_()

    def startConnection(self):
        result = self.validateInputs()
        if result[0]:
            self.button_connect.setEnabled(False)
            self.label_connection_info.setText("Status:Attempting to connect to server...")
            self.user = User(self.text_username.text(),self.text_bio.text())
            self.client = Client(self.user,self.text_ipaddr.text(),int(self.text_port.text()))
            res = self.client.connect_to_server()
            if res[0]:
                #Display new window here now, but just update status for now
                self.label_connection_info.setText("Status:Connected! Sending user info...")
                self.client.send_user_info(self.user)
            else:
                self.errBox("Connection error",res[1])
                self.button_connect.setEnabled(True)
                self.label_connection_info.setText("Status:Waiting for input...")
            
        else:
            self.errBox("Input error!",result[1])

    def retranslateUi(self, LoginWindow):
        _translate = QtCore.QCoreApplication.translate
        LoginWindow.setWindowTitle(_translate("LoginWindow", "PyRC Login"))
        self.label_title.setText(_translate("LoginWindow", "PyRC Client"))
        self.label_info.setText(_translate("LoginWindow", "A Python chat application made by Charles Hampton-Evans"))
        self.label_serverIP.setText(_translate("LoginWindow", "Server IP:"))
        self.label_port.setText(_translate("LoginWindow", "Port:"))
        self.label_username.setText(_translate("LoginWindow", "Username:"))
        self.label_bio.setText(_translate("LoginWindow", "Bio:"))
        self.button_connect.setText(_translate("LoginWindow", "Connect"))
        self.label_connection_info.setText(_translate("LoginWindow", "Status:Waiting for input..."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    LoginWindow = QtWidgets.QMainWindow()
    ui = Ui_LoginWindow()
    ui.setupUi(LoginWindow)
    LoginWindow.show()
    sys.exit(app.exec_())
