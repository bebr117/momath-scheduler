import pandas as pd
import numpy as np
from functools import partial

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget, QMainWindow, QComboBox, QLabel, QPushButton, QLineEdit
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QToolBar, QAction, QStatusBar
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, pyqtSignal

app = QApplication([])

shifts=["Float","0","-1","Security","Greet","Tickets","Lunch","Coro","Trike","Gallery"]
people=["Brian","Ross","Will"]

def minutes_to_hhmm(mins):
    hours = mins//60
    minutes = mins%60
    return f'{hours:02d}:{minutes:02d}'

def minutes_to_12h(mins):
    mins%=1440
    
    hours = mins//60
    minutes = mins%60
    if hours == 0:
        h = "12"
        ampm = "AM"
    elif hours < 12:
        h = f'{hours:02d}'
        ampm = "AM"
    elif hours == 12:
        h = "12"
        ampm = "PM"
    else:
        h2 = hours-12
        h = f'{h2:02d}'
        ampm = "PM"
    
    return h + f':{minutes:02d}' + ' ' + ampm

start_time = 600
end_time = 1020
default_schedule = pd.DataFrame("Float", index=range(start_time,end_time,30),columns=people)

class ShiftSelector(QWidget):
    shiftChanged = pyqtSignal(str)
    # textboxChanged = pyqtSignal(str)
    durationChanged = pyqtSignal(str)
    
    def __init__(self, person, start_time, shifts, durations):
        super(ShiftSelector, self).__init__()
        
        self.person = person
        self.start_time = start_time
        self.shifts = shifts
        self.durations = durations
        
        self.active = True
        
        # shift dropdown
        shift_box = QComboBox()
        shift_box.addItems(shifts)
        shift_box.addItem("Other")
        
        shift_box.currentTextChanged.connect(self.shift_changed)
        
        self.shift_box = shift_box
        
        # other shift textbox
        text_box = QLineEdit()
        text_box.setVisible(False)
        
        text_box.textChanged.connect(self.textbox_changed)
        
        self.text_box = text_box
        
        # duration dropdown
        duration_box = QComboBox()
        duration_box.addItems(durations)
        
        duration_box.currentTextChanged.connect(self.duration_changed)
        
        self.duration_box = duration_box
        
        # layout
        leftSide = QVBoxLayout()
        leftSide.addWidget(shift_box)
        leftSide.addWidget(text_box)
        leftSide.setContentsMargins(5,5,5,5)
        leftWidget = QWidget()
        leftWidget.setLayout(leftSide)
        
        rightSide = QVBoxLayout()
        rightSide.addWidget(QLabel("Duration"))
        rightSide.addWidget(duration_box)
        rightSide.setContentsMargins(0,5,5,5)
        rightWidget = QWidget()
        rightWidget.setLayout(rightSide)
        
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(leftWidget)
        mainLayout.addWidget(rightWidget)
        mainLayout.setContentsMargins(0,0,0,0)
        
        self.mainLayout = mainLayout
        self.simpleLayout = leftSide
        
        self.setLayout(self.simpleLayout)
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setPalette(palette)
    
    # TODO: add color changing to shift_changed/textbox_changed 
    
    def set_shift(self,shift):
        if shift in self.shifts:
            self.shift_box.setCurrentText(shift)
        else:
            self.shift_box.setCurrentText("Other")
            self.text_box.setText(shift)
    
    def shift_changed(self, shift):
        if shift == "Other":
            self.text_box.setEnabled(True)
            self.text_box.setVisible(True)
        else:
            self.text_box.setEnabled(False)
            self.text_box.setVisible(False)
            self.shiftChanged.emit(shift)
            
    def textbox_changed(self, text):
        self.shiftChanged.emit(text)
    
    def duration_changed(self, duration):
        self.durationChanged.emit(duration)

class CentralGrid(QWidget):
    def __init__(self, schedule, shifts):
        super(CentralGrid, self).__init__()
        
        self.schedule = schedule
        self.shifts = shifts
        
        layout = QGridLayout()
        widget_grid = dict()
        
        # Names at the top
        for i in range(schedule.shape[1]):
            layout.addWidget(QLabel(schedule.columns[i]), 0, i+1)
            widget_grid[schedule.columns[i]] = dict() # initialize the interior of the widget storage
        
        # Times at the left
        for i in range(schedule.shape[0]):
            layout.addWidget(QLabel(minutes_to_12h(schedule.index[i])),i+1,0)
        
        # Dropdowns in the middle
        for i in range(schedule.shape[0]):
            time = schedule.index[i]
            
            durations = [repr(30+schedule.index[k]-time) for k in range(i,schedule.shape[0])] # this is very scuffed lol
            for j in range(schedule.shape[1]):
                person = schedule.columns[j]
                
                widget = ShiftSelector(person, time, shifts, durations)
                widget.set_shift(self.schedule[person][time])
                
                widget.shiftChanged.connect(partial(self.updateSchedule,schedule.columns[j],schedule.index[i]))
                layout.addWidget(widget, i+1, j+1)
                widget_grid[person][time] = widget
        
        main_height = schedule.shape[0]+1
        main_width = schedule.shape[1]+1
        
        # Column shift counters
        colCounters = {p:QLabel("") for p in schedule.columns} # TODO just make the list of people an input to the grid
        colShift = ShiftSelector(None, None, shifts, [])
        # colShift.shiftChanged.connect(updateCounters)
        layout.addWidget(colShift, main_height, 0)
        for i in range(schedule.shape[1]):
            layout.addWidget(colCounters[schedule.columns[i]],main_height,i+1)
            
        # Row shift counters
        rowCounters = {t:QLabel("") for t in schedule.index} # TODO make the list of times an input as well?
        rowShift = ShiftSelector(None, None, shifts, [])
        # colShift.shiftChanged.connect(updateCounters)
        layout.addWidget(rowShift, 0, main_width)
        for i in range(schedule.shape[0]):
            layout.addWidget(rowCounters[schedule.index[i]],i+1,main_width)
        
        # TEMPORARY: add a "print" button in the top-left
        # Maybe change this to a save button later?
        widget = QPushButton("Print")
        widget.pressed.connect(self.printSchedule)
        layout.addWidget(widget, 0, 0)
        
        layout.setSpacing(5)
        
        self.layout = layout
        self.widget_grid = widget_grid
        self.setLayout(layout)
    
    def updateSchedule(self, person, time, shift):
        self.schedule[person][time] = shift
        # TODO add something about durations?
        
    # def updateCounters(self):
    #     for 
        
    def printSchedule(self):
        print(self.schedule)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.setWindowTitle("MoMath Schedule Manager")
        
        widget = CentralGrid(default_schedule, shifts)
        
        self.setCentralWidget(widget)
        # TODO change default margins

w = MainWindow()
w.show()

app.exec()