#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import json
import time
from subprocess import Popen, PIPE
import os
from datetime import date, datetime
from PyQt5.QtWidgets import (QWidget, QApplication, QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit, 
                             QVBoxLayout, QPushButton, QToolBar, QMessageBox, QLabel, QMainWindow)
from PyQt5.QtCore import Qt, QDir

import tv_hoerzu_jetzt_tv
import tv_hoerzu_gleich_tv


class Viewer(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setStyleSheet(myStyleSheet(self))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)
        layout = QVBoxLayout()
        self.title = QLabel()
        layout.addWidget(self.title)
        layout.addWidget(self.viewer)
        self.setLayout(layout)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        
   
class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        self.setMinimumSize(500, 300)
        self.table = QTableWidget()
        #self.table.setSelectionBehavior(2)
        self.table.horizontalScrollBar().setVisible(False)
        self.table.verticalScrollBar().setVisible(False)
        
        self.setStyleSheet(myStyleSheet(self))
        self.chList = []       
        ### Zugehörige ID
        self.idList = []
        
        self.dictList = {'ard': 71, 'zdf': 37, 'zdf neo': 659, 'zdf info': 276, 'arte': 58, \
                        'wdr': 46, 'ndr': 47, 'mdr': 48, 'hr': 49, 'swr': 10142, 'br': 51, \
                        'rbb': 52, '3sat': 56,'alpha': 104, 'kika': 57, 'phoenix': 194, \
                        'tagesschau': 100, 'one': 146, 'rtl': 38, 'sat 1': 39, 'pro 7': 40,\
                        'rtl plus': 12033, 'kabel 1': 44, 'rtl 2': 41, 'vox': 42, 'rtl nitro': 763, \
                        'n24 doku': 12045, 'kabel 1 doku': 12043, 'sport 1': 64, 'super rtl': 43, \
                        'sat 1 gold': 774, 'vox up': 12125, 'sixx': 694, 'servus tv': 660, \
                        'welt': 175, 'orf 1': 54, 'orf 2': 55, 'orf 3': 56, 'rtl passion': 529, \
                        'rtl crime': 527, 'srf 1': 59, 'srf 2': 60, 'srf info': 231}
        
        for key, value in self.dictList.items():
            self.chList.append(key)
            self.idList.append(value)
        
        count = len(self.chList)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(count)
        for column in range(count):
            header = QTableWidgetItem(self.chList[column].upper())
            self.table.setHorizontalHeaderItem(column, header)
        self.table.horizontalHeader().sectionClicked.connect(self.selectTime)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        cw = QWidget()
        cw.setLayout(layout)
        self.setCentralWidget(cw)
        
        tbf = QToolBar("Tools")
        tbf.setContextMenuPolicy(Qt.PreventContextMenu)
        tbf.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, tbf)
        empty = QWidget()
        empty.setFixedWidth(72)
        tbf.addWidget(empty)
        self.findfield = QLineEdit(placeholderText = "find", clearButtonEnabled = True, returnPressed = self.findMe)
        self.findfield.setFixedWidth(180)
        tbf.addWidget(self.findfield)
        tbf.addSeparator()
        
        actNow = QPushButton("Jetzt", self, clicked = self.doNow)
        actNow.setFixedWidth(70)
        tbf.addWidget(actNow)
        
        actNext = QPushButton("Danach", self, clicked = self.doNext)
        actNext.setFixedWidth(70)
        tbf.addWidget(actNext)
        
        act15 = QPushButton("15:00", self, clicked = lambda: self.doTime("15:"))
        act15.setFixedWidth(70)
        tbf.addWidget(act15)
        
        act16 = QPushButton("16:00", self, clicked = lambda: self.doTime("16:"))
        act16.setFixedWidth(70)
        tbf.addWidget(act16)
        
        act18 = QPushButton("18:00", self, clicked = lambda: self.doTime("18:"))
        act18.setFixedWidth(70)
        tbf.addWidget(act18)
        
        actAbend = QPushButton("20:15", self, clicked = lambda: self.doTime("20:15"))
        actAbend.setFixedWidth(70)
        tbf.addWidget(actAbend)
        
        act22 = QPushButton("22:00", self, clicked = lambda: self.doTime("22:"))
        act22.setFixedWidth(70)
        tbf.addWidget(act22)
        
        actReload = QPushButton("reload", self, clicked = self.reload)
        actReload.setFixedWidth(70)
        tbf.addWidget(actReload)

        tb = QToolBar("Sender 1")
        tb.setContextMenuPolicy(Qt.PreventContextMenu)
        tb.setMovable(False)
        self.addToolBar(Qt.LeftToolBarArea, tb)

        for b in range(18):
            name = self.chList[b].upper()
            act = QPushButton(name, self, clicked = self.showMe)
            act.setFixedWidth(70)
            act.setObjectName(name)
            tb.addWidget(act)
            
        self.addToolBarBreak()

        tb2 = QToolBar("Sender 2")
        tb2.setContextMenuPolicy(Qt.PreventContextMenu)
        tb2.setMovable(False)
        self.addToolBar(Qt.RightToolBarArea, tb2)     
        for b in range(18, len(self.chList)):
            name = self.chList[b].upper()
            act = QPushButton(name, self, clicked = self.showMe)
            act.setFixedWidth(70)
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
        
    def reload(self):
        self.table.clear()
        url = "http://mobile.hoerzu.de/programbystation"
        ### temporär speichern
        myfile = os.path.join(QDir.homePath(), "prg.json")
        #basedate = str(date.today())
        now = datetime.now()
        td = now.strftime("%-d.%B %Y")
        self.hour = now.strftime("%H")
        print("Stunde", self.hour)
        self.setWindowTitle("%s - %s" %("TV Programm heute", td))
        ### überprüfen ob Datei existiert
        cmd = ["wget", url, "-O", myfile]
        print("hole neue Datei")
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
            header = QTableWidgetItem(self.chList[column].upper())
            self.table.setHorizontalHeaderItem(column, header)  
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
                            msg = "%s um %s" %(header, self.table.item(row, column).text().replace(" ", " Uhr: ", 1))
                            findList.append(msg)
                                
            if not findList == []:
                text = '\n'.join(findList)
                self.v = Viewer()
                self.v.viewer.setText(text)
                self.v.setGeometry(100, 50, 400, 400)
                self.v.title.setText("<h1>Suchergebnis</h1>(Schließen mit Escape)")
                self.v.show()
            else:
                self.msgbox("Suchergebnis", "nichts gefunden!")
                
    def doTime(self, ft):
        findList = []
        print("suche nach", ft)
        for row in range(self.table.rowCount()):
            for column in range(self.table.columnCount()):
                if not self.table.item(row, column) == None:
                    if ft in self.table.item(row, column).text():
                        header = self.table.horizontalHeaderItem(column).text()
                        h = int(self.hour)
                        m = self.table.item(row, column).text().replace("20:15 ", "", 1)
                        msg = "<b>head</b><br>msg<br>"
                        ms = msg.replace("head", header).replace("msg", m)
                        findList.append(ms)
                            
        if not findList == []:
            text = '\n'.join(findList)
            self.v = Viewer()
            self.v.viewer.setText(text)
            self.v.setGeometry(100, 50, 700, 600)
            title = "<h1>Programm nach mmm Uhr</h1>(Schließen mit Escape)"
            if len(ft) > 4:
                self.v.title.setText(title.replace("mmm", ft))
            else:
                self.v.title.setText(title.replace("mmm", ft + "00"))
            self.v.show()
        else:
            self.msgbox("Suchergebnis", "nichts gefunden!")  
        
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
        self.table.clearSelection()
        h = int(self.hour + "00")
        k = h - 60
        m = h + 90
        for row in range(self.table.rowCount()):
            if self.table.item(row, column) == None:
                self.table.setItem(row, column, QTableWidgetItem(" "))
                self.table.item(row, column).setSelected(False)
                
            if self.table.item(row, column) == ' ':
                self.table.item(self.table.rowCount(), column).setSelected(False)
            rowtext = str(self.table.item(row, column).text().partition(" ")[0].replace(":", ""))
            if not rowtext == "":
                mt = int(rowtext)
                if mt > k and mt < m:
                    self.table.item(row, column).setSelected(True)
                    self.table.scrollToItem(self.table.selectedItems()[0], 1)
                else:
                    self.table.item(row, column).setSelected(False)
        #for row in range(self.table.rowCount()):
        if self.table.selectedItems() == []:
            h = int(self.hour + "00")
            k = h - 95
            m = h
            for row in range(self.table.rowCount()):
                if self.table.item(row, column) == None:
                    self.table.setItem(row, column, QTableWidgetItem(" "))
                    self.table.item(row, column).setSelected(False)
                    
                if self.table.item(row, column) == ' ':
                    self.table.item(self.table.rowCount(), column).setSelected(False)
                rowtext = str(self.table.item(row, column).text().partition(" ")[0].replace(":", ""))
                if not rowtext == "":
                    mt = int(rowtext)
                    if mt > k and mt < m:
                        self.table.item(row, column).setSelected(True)
                        self.table.scrollToItem(self.table.selectedItems()[0], 1)
                    else:
                        self.table.item(row, column).setSelected(False)                

                    
    def msgbox(self, title, message):
        msg = QMessageBox(1, title, message, QMessageBox.Ok)
        msg.exec()
        
    def doNow(self):
        text = tv_hoerzu_jetzt_tv.do()
        self.v = Viewer()
        self.v.title.setText("<h1>jetzt im TV</h1>(Schließen mit Escape)")
        self.v.setGeometry(100, 40, 700, 600)
        self.v.viewer.setText(text)
        self.v.show()
        self.v.viewer.setFocus()

    def doNext(self):
        text = tv_hoerzu_gleich_tv.do()
        self.v = Viewer()
        self.v.viewer.setText(text)
        self.v.title.setText("<h1>demnächst im TV</h1>(Schließen mit Escape)")
        self.v.setGeometry(100, 50, 700, 600)
        self.v.show()
        self.v.viewer.setFocus()
        
def myStyleSheet(self):
    return """
QMenu::item:hover
{
color: #729fcf;
}
QLabel
{
color: #729fcf;
font-size: 10px;
}
QWidget
{
background: #2e3436;
}
QTextEdit
{
font-size: 11px;
background: #2e3436;
border: 1px solid #1a2334;
color: #d3d7cf;
} 
QTableWidget
{
font-size: 10px;
background: #2e3436;
selection-color: #1a2334;
border: 1px solid #1a2334;
selection-background-color: #729fcf;
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
    window.showMaximized()
    sys.exit(app.exec_())
    
