#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import json
import time
from subprocess import Popen, PIPE
import os
from datetime import date, datetime
from PyQt5.QtWidgets import (QWidget, QApplication, QTableWidget, QTableWidgetItem, QLineEdit, 
                             QVBoxLayout, QAction, QPushButton, QToolBar, QMessageBox, QMainWindow)
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QIcon
   
class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        self.setMinimumSize(500, 300)
        self.table = QTableWidget()
        #self.table.setSelectionBehavior(2)
        self.table.horizontalScrollBar().setVisible(False)
        self.table.verticalScrollBar().setVisible(False)
        self.setStyleSheet(myStyleSheet(self))
        self.chList = ["ard","zdf","arte","zdf neo","zdf info","wdr","ndr","mdr","hr","swr","br",\
            "rbb","3sat","kika","phoenix","tagesschau","one", "rtl", "sat 1", "pro 7", "kabel 1", \
            "rtl 2", "vox", "rtl nitro", "n24 doku", "kabel 1 doku", "sport 1", "super rtl", \
            "sat 1 gold", "vox up", "sixx", "servus tv", "super rtl"]       
        ### Zugehörige ID bei hoerzu
        self.idList = [71,37,58,659,276,46,47,48,49,10142,51,52,56,57,194,100,146,38,39,40,44,41,42,763,12045,12043,64,12033,774,12125,694,660,43]
        count = len(self.chList)
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(count)
        for column in range(count):
            header = QTableWidgetItem(self.chList[column].upper())
            self.table.setHorizontalHeaderItem(column, header)
            
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        cw = QWidget()
        cw.setLayout(layout)
        self.setCentralWidget(cw)

        tb = QToolBar("Sender 1")
        self.addToolBar(Qt.LeftToolBarArea, tb)
        tb.setContextMenuPolicy(Qt.PreventContextMenu)
        tb.setMovable(True)
        self.findfield = QLineEdit(placeholderText = "find", clearButtonEnabled = True, returnPressed = self.findMe)
        self.findfield.setFixedWidth(80)
        tb.addWidget(self.findfield)
        for b in range(16):
            name = self.chList[b].upper()
            act = QPushButton(name, self, clicked = self.showMe)
            act.setObjectName(name)
            tb.addWidget(act)
            
        br = self.addToolBarBreak()

        tb2 = QToolBar("Sender 2")
        self.addToolBar(Qt.LeftToolBarArea, tb2)     
        for b in range(17, len(self.chList)):
            name = self.chList[b].upper()
            act = QPushButton(name, self, clicked = self.showMe)
            act.setObjectName(name)
            tb2.addWidget(act)

        url = "http://mobile.hoerzu.de/programbystation"
        ### temporär speichern
        myfile = os.path.join(QDir.homePath(), "prg.json")
        basedate = str(date.today())
        now = datetime.now()
        td = now.strftime("%-d.%B %Y")
        self.hour = now.strftime("%H")
        print("Stunde", self.hour)
        self.setWindowTitle("%s - %s" %("TV Programm heute", td))
        ### überprüfen ob Datei existiert
        cmd = ["wget", url, "-O", myfile]
        if os.path.isfile(myfile):
            used = os.stat(myfile).st_mtime
            st = time.strftime("%Y-%m-%d", time.localtime(used))
            ### überprüfen ob Datei aktuell ist
            if not basedate == st:
                print("Datei nicht aktuell, hole neue Datei")
                process = Popen(cmd, stdout=PIPE, stderr=PIPE)
                stdout, stderr = process.communicate()
            else:
                print("Datei ist aktuell")
        else:
            print("Datei nicht vorhanden, hole neue Datei")
            process = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            
        text = open(myfile).read()
        self.parsed = json.loads(text)
        
        ### Programm aller Kanäle in der Liste 
        self.table.setRowCount(36)

        for x in range(len(self.idList)):
            p = self.getValues(self.idList[x], x)
            
        for column in range(self.table.columnCount()):
            self.table.resizeColumnToContents(column)
  
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeRowsToContents()
        
    def findMe(self):
        if not self.findfield.text() == "":
            ft = [self.findfield.text(), self.findfield.text().lower(), self.findfield.text().upper(), self.findfield.text().title()]
            findList = []
            print("suche nach", ft)
            for row in range(self.table.rowCount()):
                for column in range(self.table.columnCount()):
                    if not self.table.item(row, column) == None:
                        if ft[0] in self.table.item(row, column).text() \
                        or ft[1] in self.table.item(row, column).text() \
                        or ft[2] in self.table.item(row, column).text() \
                        or ft[3] in self.table.item(row, column).text():
                            header = self.table.horizontalHeaderItem(column).text()
                            h = int(self.hour)
                            #if int(self.table.item(row, column).text().partition(":")[0]) > h-1:
                            msg = "%s um %s" %(header, self.table.item(row, column).text().replace(" ", " Uhr: ", 1))
                            findList.append(msg)
            if not findList == []:
                self.msgbox('\n'.join(findList))
            else:
                self.msgbox("nichts gefunden!")
        
    def showMe(self, *args):
        name = self.sender().objectName().upper()
        print("clicked:", name)
        for column in range(self.table.columnCount()):
            if self.table.horizontalHeaderItem(column).text() == name:
                self.table.selectColumn(column)
                self.selectTime(column)
        

    def getValues(self, channel, column):
        row = 0
        p = ""
        for i in self.parsed:
            if i['id'] == channel:
                pr = i['broadcasts']
                for a in pr:
                    title = str(a.get('title'))
                    st = a.get('startTime')
                    start = time.strftime("%-H:%M", time.localtime(st))
                    p = QTableWidgetItem("%s %s" % (start, title))
                    self.table.setItem(row, column, p)
                    row = row + 1
                #break
        self.table.selectColumn(0)
        self.selectTime(0)
        
        
    def selectTime(self, column):
        h = int(self.hour + "00")
        for row in range(self.table.rowCount()):
            if self.table.item(row, column) == None:
                self.table.setItem(row, column, QTableWidgetItem(" "))
                self.table.item(row, column).setSelected(False)
                
            if self.table.item(row, column) == ' ':
                self.table.item(self.table.rowCount(), column).setSelected(False)
  
            if self.table.item(row, column).text().startswith(str(h)[:2]):
                self.table.item(row, column).setSelected(True)
                self.table.scrollToItem(self.table.selectedItems()[0], 1)
            else:
                self.table.item(row, column).setSelected(False)

                    
    def msgbox(self, message):
        msg = QMessageBox(1, "Ergebnis", message, QMessageBox.Ok)
        msg.exec()

        
def myStyleSheet(self):
    return """
QTableWidget
{
font-size: 10px;
background: #2e3436;
selection-color: #eeeeec;
border: 1px solid #1a2334;
selection-background-color: #1a2334;
color: #d3d7cf;
outline: 0;
} 
QHeaderView::section
{background-color:#2e3436;
color: #d3d7cf; 
font: bold
}

QTableCornerButton::section 
{
background-color:#d3d7cf; 
}
QStatusBar
{
font-size: 8pt;
color: #555753;
}
QMenuBar
{
background: transparent;
border: 0px;
}
QToolBar
{
background: transparent;
border: 0px;
}
QMainWindow
{
background: #2e3436;
}
QPushButton
{
font-size: 9px;
background: #202020;
color: #eeeeec;
}
QPushButton::hover{
background: #c4a000;
color: #202020;
}
QScrollBar:vertical 
{
width: 10px; 
}
QScrollBar:horizontal 
{
height: 10px; 
}
QLineEdit
{
background: #2e3436;
color: #eeeeec;
}
    """          
  
if __name__ == '__main__':
  
    app = QApplication(sys.argv)
    window = Window()
    window.setGeometry(0, 0, 900, 600)
    window.show()
    sys.exit(app.exec_())
    
