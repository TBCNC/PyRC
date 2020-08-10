# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chat_window.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ChatWindow(object):
    def setupUi(self, ChatWindow):
        ChatWindow.setObjectName("ChatWindow")
        ChatWindow.resize(808, 440)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ChatWindow.sizePolicy().hasHeightForWidth())
        ChatWindow.setSizePolicy(sizePolicy)
        ChatWindow.setDocumentMode(False)
        self.centralwidget = QtWidgets.QWidget(ChatWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.text_messages = QtWidgets.QTextEdit(self.centralwidget)
        self.text_messages.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.text_messages.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.text_messages.setObjectName("text_messages")
        self.gridLayout.addWidget(self.text_messages, 0, 0, 2, 1)
        self.label_usersonline = QtWidgets.QLabel(self.centralwidget)
        self.label_usersonline.setObjectName("label_usersonline")
        self.gridLayout.addWidget(self.label_usersonline, 0, 1, 1, 1)
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setMaximumSize(QtCore.QSize(150, 16777215))
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 1, 1, 1, 2)
        self.input_message = QtWidgets.QLineEdit(self.centralwidget)
        self.input_message.setObjectName("input_message")
        self.gridLayout.addWidget(self.input_message, 2, 0, 1, 2)
        self.button_send = QtWidgets.QPushButton(self.centralwidget)
        self.button_send.setObjectName("button_send")
        self.gridLayout.addWidget(self.button_send, 2, 2, 1, 1)
        ChatWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ChatWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 808, 21))
        self.menubar.setObjectName("menubar")
        ChatWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ChatWindow)
        self.statusbar.setObjectName("statusbar")
        ChatWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ChatWindow)
        QtCore.QMetaObject.connectSlotsByName(ChatWindow)

    def retranslateUi(self, ChatWindow):
        _translate = QtCore.QCoreApplication.translate
        ChatWindow.setWindowTitle(_translate("ChatWindow", "ChatWindow"))
        self.label_usersonline.setText(_translate("ChatWindow", "Users Online:"))
        self.button_send.setText(_translate("ChatWindow", "Send"))
    def addChatMessage(self,user,message):
        self.text_messages.moveCursor(QtGui.QTextCursor.End)
        self.text_messages.insertPlainText("<{}>:{}\n".format(user,message))
    def addUser(self,user):
        self.listWidget.addItem(user)
    def removeUser(self,user):
        itemstoremove = self.listWidget.findItems(user,QtCore.Qt.MatchExactly)
        for item in itemstoremove:
            row = self.listWidget.row(item)
            self.listWidget.takeItem(row)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ChatWindow = QtWidgets.QMainWindow()
    ui = Ui_ChatWindow()
    ui.setupUi(ChatWindow)
    ChatWindow.show()
    sys.exit(app.exec_())
