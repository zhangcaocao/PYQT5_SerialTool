# -*- coding: utf-8 -*-
import binascii
import random
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.Qt import *
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import *
from scipy import interpolate

import queue


datalist = []
num = 0

DATAQUEUE = queue.Queue()


TITLE = "串口调试助手"
ABOUT_TITLE = "电压显示"
ABOUT_STRING = "https://github.com/zhangcaocao/PYQT5_SerialTool"

class PyQt_Serial(QTabWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.DataTab=QWidget()
        self.PlotTab=QWidget()
        # self.tab3=QWidget()

        self.addTab(self.DataTab, "数据显示")
        self.addTab(self.PlotTab, "图像绘制")
        # self.addTab(self.tab3, "Tab 3")


        self.CreateItems()
        self.CreateLayout()
        self.CreateSignalSlot()

        self.Init_PlotUI()

        self.setWindowTitle('串口调试助手')
        self.setWindowIcon(QIcon('./icon.png'))
        self.setFont(QFont('宋体', 9))

        self.sendCount = 0
        self.receiveCount = 0
        self.encoding = 'utf-8'
        self.updateTimer.start(100)

    def CreateItems(self):
        self.com = QSerialPort()

        self.comNameLabel = QLabel('串口号')
        self.comNameLabel.setFixedWidth(80)
        self.comNameCombo = QComboBox()
        self.on_refreshCom()

        self.comNameCombo.setFixedWidth(80)
        self.baudLabel = QLabel('波特率')
        self.baudLabel.setFixedWidth(80)
        self.baudCombo = QComboBox()
        self.baudCombo.addItems(
            ('9600', '19200', '115200', '250000', '1000000'))
        self.baudCombo.setEditable(True)
        self.baudCombo.setCurrentIndex(2)
        self.baudCombo.setFixedWidth(80)
        self.bupt = QLabel('')  # BUPT
        self.bupt.setFont(QFont('Arial', 40, italic=True))

        self.comencodingLabel = QLabel('串口编码')
        # self.comencodingCombo = QComboBox()
        # self.comencodingCombo.addItems(('UTF-8', 'GBK'))
        self.UTF8Button = QRadioButton('UTF-8')
        self.GBKButton = QRadioButton('GBK')
        self.encodingGroup = QButtonGroup()
        self.encodingGroup.addButton(self.UTF8Button, 0)
        self.encodingGroup.addButton(self.GBKButton, 1)
        self.UTF8Button.setChecked(True)
        self
        self.openButton = QPushButton('打开串口')
        self.openButton.setFixedWidth(80)
        self.closeButton = QPushButton('关闭串口')
        self.closeButton.setFixedWidth(80)
        self.clearReceivedButton = QPushButton('清除接收缓冲区')
        self.clearReceivedButton.setFixedWidth(165)
        self.stopShowingButton = QPushButton('停止显示')
        self.stopShowingButton.setFixedWidth(165)
        self.hexShowingCheck = QCheckBox('十六进制显示')
        self.hexShowingCheck.setFixedWidth(165)
        self.saveReceivedButton = QPushButton('保存显示数据')
        self.saveReceivedButton.setFixedWidth(165)
        self.openButton = QPushButton('打开串口')
        self.openButton.setFocus()
        self.openButton.setFixedWidth(80)
        self.closeButton = QPushButton('关闭串口')
        self.closeButton.setFixedWidth(80)
        self.refreshComButton = QPushButton('刷新串口')
        self.aboutButton = QPushButton('关于')
        self.aboutButton.setFixedWidth(80)
        self.PlotButton = QPushButton('绘图')
        self.PlotButton.setFixedWidth(80)

        self.receivedDataEdit = QPlainTextEdit()
        self.receivedDataEdit.setReadOnly(True)
        self.receivedDataEdit.setFont(QFont('Courier New', 11))

        self.inputEdit = QPlainTextEdit()
        self.inputEdit.setFixedHeight(70)
        self.inputEdit.setFont(QFont('Courier New', 11))
        self.sendButton = QPushButton('发送')
        self.sendButton.setFixedWidth(105)
        self.sendButton.setFixedHeight(70)
        self.hexSendingCheck = QCheckBox('十六进制发送')
        self.timerSendCheck = QCheckBox('定时发送   发送周期(毫秒)')
        self.timerPeriodEdit = QLineEdit('1000')
        self.spacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.clearInputButton = QPushButton('清空重填')
        self.clearCouterButton = QPushButton('计数清零')

        self.comStatus = QLabel('串口状态：COM  关闭')
        self.sendCountLabel = QLabel('发送计数：0')
        self.receiveCountLabel = QLabel('接收计数：0')

        self.sendTimer = QTimer()
        self.updateTimer = QTimer()

        self.closeButton.setEnabled(False)
        self.sendButton.setEnabled(False)
        
    def CreateLayout(self):
        self.mainLayout = QGridLayout()

        self.mainLayout.addWidget(self.comNameLabel, 0, 0)
        self.mainLayout.addWidget(self.comNameCombo, 0, 1)
        self.mainLayout.addWidget(self.baudLabel, 1, 0)
        self.mainLayout.addWidget(self.baudCombo, 1, 1)
        self.mainLayout.addWidget(self.comencodingLabel, 2, 0)
        # self.mainLayout.addWidget(self.comencodingCombo, 2, 1)
        self.mainLayout.addWidget(self.UTF8Button, 3, 0)
        self.mainLayout.addWidget(self.GBKButton, 3, 1)
        self.mainLayout.addWidget(self.openButton, 5, 0)
        self.mainLayout.addWidget(self.closeButton, 5, 1)
        self.mainLayout.addWidget(self.refreshComButton, 6, 0, 1, 2)
        self.mainLayout.addWidget(self.clearReceivedButton, 7, 0, 1, 2)
        self.mainLayout.addWidget(self.stopShowingButton, 8, 0, 1, 2)
        self.mainLayout.addWidget(self.hexShowingCheck, 9, 0, 1, 2)
        self.mainLayout.addWidget(self.saveReceivedButton, 10, 0, 1, 2)
        self.mainLayout.addWidget(self.aboutButton, 11, 0)
        self.mainLayout.addWidget(self.PlotButton, 11, 1)

        self.mainLayout.addWidget(self.receivedDataEdit, 0, 2, 12, 6)

        self.mainLayout.addWidget(self.inputEdit, 12, 0, 1, 7)
        self.mainLayout.addWidget(self.sendButton, 12, 7)
        self.mainLayout.addWidget(self.hexSendingCheck, 13, 0, 1, 2)
        self.mainLayout.addWidget(self.timerSendCheck, 13, 2, 1, 2)
        self.mainLayout.addWidget(self.timerPeriodEdit, 13, 4)
        self.mainLayout.addItem(self.spacer, 13, 5)
        self.mainLayout.addWidget(self.clearInputButton, 13, 6)
        self.mainLayout.addWidget(self.clearCouterButton, 13, 7)
        self.mainLayout.addWidget(self.comStatus, 14, 0, 1, 3)
        self.mainLayout.addWidget(self.sendCountLabel, 14, 4, 1, 2)
        self.mainLayout.addWidget(self.receiveCountLabel, 14, 6, 1, 2)
        self.mainLayout.setSpacing(5)

        # self.setLayout(self.mainLayout)
        self.setFixedSize(700, self.height())
        self.DataTab.setLayout(self.mainLayout)
    def CreateSignalSlot(self):
        self.openButton.clicked.connect(self.on_openSerial)  # 打开串口
        self.closeButton.clicked.connect(self.on_closeSerial)  # 关闭串口
        self.com.readyRead.connect(self.on_receiveData)  # 接收数据
        self.sendButton.clicked.connect(self.on_sendData)  # 发送数据
        self.refreshComButton.clicked.connect(self.on_refreshCom)  # 刷新串口状态
        self.aboutButton.clicked.connect(self.on_aboutButton)  # 修改记录
        # self.PlotButton.clicked.connect(self.on_plotData)  # 关于PyQt
        self.clearInputButton.clicked.connect(self.inputEdit.clear)  # 清空输入
        self.clearReceivedButton.clicked.connect(
            self.receivedDataEdit.clear)  # 清空接收
        self.stopShowingButton.clicked.connect(self.on_stopShowing)  # 停止显示
        self.clearCouterButton.clicked.connect(self.on_clearCouter)  # 清空计数

        self.saveReceivedButton.clicked.connect(
            self.on_saveReceivedData)  # 保存数据

        self.timerSendCheck.clicked.connect(self.on_timerSendChecked)  # 定时发送开关
        self.sendTimer.timeout.connect(self.on_sendData)  # 定时发送

        self.updateTimer.timeout.connect(self.on_updateTimer)  # 界面刷新
        self.hexShowingCheck.stateChanged.connect(
            self.on_hexShowingChecked)  # 十六进制显示
        self.timerPeriodEdit.textChanged.connect(self.on_timerSendChecked)
        self.UTF8Button.clicked.connect(self.on_setEncoding)
        self.GBKButton.clicked.connect(self.on_setEncoding)

        self.hexSendingCheck.stateChanged.connect(
            self.on_hexSendingChecked)  # 十六进制发送

    def Init_PlotUI(self):

        self.PlotLayout = QGridLayout()
        self.PlotButton.clicked.connect(self.on_plot)  # 绘图
        self.pw = pg.PlotWidget()
        self.pw.showGrid(x=True, y=True)
        self.PlotLayout.addWidget(self.pw)
        self.PlotTab.setLayout(self.PlotLayout)

    def on_plot(self):
        # print (datalist)
        timer = QTimer(self)
        timer.timeout.connect(self.update_plot)
        timer.start(0)
    
    def update_plot(self):
        # print (datalist)
        # data_list = list(float(i) for i in datalist)
        global num
        if len(datalist):
            data_list = list(float(i) for i in datalist)
            # data = float(datalist.pop(0))
            # print (data)
            pg.QtGui.QApplication.processEvents()
            
            self.pw.plot(data_list, pen='r', clear=True, symbol='d')
            num = num + 1
        pass

    def on_refreshCom(self):
        self.comNameCombo.clear()
        com = QSerialPort()
        for info in QSerialPortInfo.availablePorts():
            com.setPort(info)
            if com.open(QSerialPort.ReadWrite):
                self.comNameCombo.addItem(info.portName())
                com.close()

    def on_setEncoding(self):
        if self.encodingGroup.checkedId() == 0:
            self.encoding = 'utf-8'
        else:
            self.encoding = 'gbk'

    def on_openSerial(self):
        comName = self.comNameCombo.currentText()
        comBaud = int(self.baudCombo.currentText())
        self.com.setPortName(comName)

        try:
            if self.com.open(QSerialPort.ReadWrite) == False:
                QMessageBox.critical(self, '严重错误', '串口打开失败')
                return
        except:
            QMessageBox.critical(self, '严重错误', '串口打开失败')
            return

        self.com.setBaudRate(comBaud)
        if self.timerSendCheck.isChecked():
            self.sendTimer.start(int(self.timerPeriodEdit.text()))

        self.openButton.setEnabled(False)
        self.closeButton.setEnabled(True)
        self.comNameCombo.setEnabled(False)
        self.baudCombo.setEnabled(False)
        self.sendButton.setEnabled(True)
        self.refreshComButton.setEnabled(False)
        self.comStatus.setText('串口状态：%s  打开   波特率 %s' % (comName, comBaud))

    def on_closeSerial(self):
        self.com.close()
        self.openButton.setEnabled(True)
        self.closeButton.setEnabled(False)
        self.comNameCombo.setEnabled(True)
        self.baudCombo.setEnabled(True)
        self.sendButton.setEnabled(False)
        self.comStatus.setText('串口状态：%s  关闭' % self.com.portName())
        if self.sendTimer.isActive():
            self.sendTimer.stop()

    def on_timerSendChecked(self):
        if self.com.isOpen():
            if self.timerSendCheck.isChecked():
                self.sendTimer.start(int(self.timerPeriodEdit.text()))
            else:
                self.sendTimer.stop()
        return

    def on_stopShowing(self):
        if self.stopShowingButton.text() == '停止显示':
            self.stopShowingButton.setText('继续显示')
        else:
            self.stopShowingButton.setText('停止显示')

    def on_clearCouter(self):
        self.sendCount = 0
        self.receiveCount = 0
        pass

    def on_updateTimer(self):
        self.sendCountLabel.setText('发送计数：%d' % self.sendCount)
        self.receiveCountLabel.setText('接收计数：%d' % self.receiveCount)
        pass

    def on_sendData(self):
        txData = self.inputEdit.toPlainText()
        if len(txData) == 0:
            return
        if self.hexSendingCheck.isChecked():

            s = txData.replace(' ', '')
            if len(s) % 2 == 1:  # 如果16进制不是偶数个字符,去掉最后一个
                QMessageBox.critical(self, '错误', '十六进制数不是偶数个')
                return
            # pattern = re.compile('[^0-9a-fA-F]')
            # r = pattern.findall(s)
            # if len(r) != 0:
            #     QMessageBox.critical(self, '错误', '包含非十六进制数')
            #     return

            if not s.isalnum():
                QMessageBox.critical(self, '错误', '包含非十六进制数')
                return

            try:
                hexData = binascii.a2b_hex(s)
            except:
                QMessageBox.critical(self, '错误', '转换编码错误')
                return

            try:
                n = self.com.write(hexData)
            except:
                QMessageBox.critical(self, '异常', '十六进制发送错误')
                return
        else:
            n = self.com.write(txData.encode(self.encoding, "ignore"))
        self.sendCount += n

    def on_receiveData(self):
        global datalist
        try:
            '''将串口接收到的QByteArray格式数据转为bytes,并用gkb或utf8解码'''
            receivedData = bytes(self.com.readAll())
        except:
            QMessageBox.critical(self, '严重错误', '串口接收数据错误')
        if len(receivedData) > 0:
            self.receiveCount += len(receivedData)
            if self.stopShowingButton.text() == '停止显示':
                if self.hexShowingCheck.isChecked() == False:
                    receivedData = receivedData.decode(self.encoding, 'ignore')
                    data_list = re.findall(r"\d+.*\d+", receivedData)
                    datalist.extend(data_list)
                    # datalist = data_list
                    # print (datalist)
                    self.receivedDataEdit.insertPlainText(receivedData)
                else:
                    data = binascii.b2a_hex(receivedData).decode('ascii')
                    pattern = re.compile('.{2,2}')
                    hexStr = ' '.join(pattern.findall(data)) + ' '
                    self.receivedDataEdit.insertPlainText(hexStr.upper())

    def on_hexShowingChecked(self):
        self.receivedDataEdit.insertPlainText('\n')

    def on_hexSendingChecked(self):
        if self.hexSendingCheck.isChecked():
            data = self.inputEdit.toPlainText().upper()
            self.inputEdit.clear()
            self.inputEdit.insertPlainText(data)

    def on_saveReceivedData(self):
        fileName, fileType = QFileDialog.getSaveFileName(
            self, '保存数据', 'data', "文本文档(*.txt);;所有文件(*.*)")
        print('Save file', fileName, fileType)

        writer = QTextDocumentWriter(fileName)
        writer.write(self.receivedDataEdit.document())

    def on_aboutButton(self):
        QMessageBox.about(self, ABOUT_TITLE, ABOUT_STRING)
    




if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = PyQt_Serial()
    win.show()
    app.exec_()
    app.exit()
