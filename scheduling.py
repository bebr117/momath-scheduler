import pandas as pd
import numpy as np
from functools import partial

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget, QMainWindow, QComboBox, QLabel, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QToolBar, QAction, QStatusBar
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

app = QApplication([])

shifts=["Float","0","-1","Security","Greet","Tickets","Lunch","Coro","Trike","Gallery","Other"]
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

class CentralGrid(QWidget):
    def __init__(self, schedule, shifts):
        super(CentralGrid, self).__init__()
        
        self.schedule = schedule
        self.shifts = shifts
        
        layout = QGridLayout()
        
        # Names at the top
        for i in range(schedule.shape[1]):
            layout.addWidget(QLabel(schedule.columns[i]), 0, i+1)
        
        # Times at the left
        for i in range(schedule.shape[0]):
            layout.addWidget(QLabel(minutes_to_12h(schedule.index[i])),i+1,0)
        
        # Dropdowns in the middle
        for i in range(schedule.shape[0]):
            time = schedule.index[i]
            for j in range(schedule.shape[1]):
                person = schedule.columns[j]
                
                widget = QComboBox()
                widget.addItems(shifts)
                widget.addItem("Other") # TODO add a few extra features to this -- probably separate into its own class
                
                # Make the dropdown show the correct shift
                current_shift = self.schedule[person][time]
                if current_shift in self.shifts:
                    widget.setCurrentText(current_shift)
                else:
                    widget.setCurrentText("Other") #TODO make this a better feature
                
                widget.currentTextChanged.connect(partial(self.updateSchedule,schedule.columns[j],schedule.index[i]))
                layout.addWidget(widget, i+1, j+1)
        
        # TEMPORARY: add a "print" button in the top-left
        # Maybe change this to a save button later?
        widget = QPushButton("Print")
        widget.pressed.connect(self.printSchedule)
        layout.addWidget(widget, 0, 0)
        
        self.setLayout(layout)
    
    def updateSchedule(self, person, time, shift):
        self.schedule[person][time] = shift
        
    def printSchedule(self):
        print(self.schedule)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.setWindowTitle("MoMath Schedule Manager")
        
        widget = CentralGrid(default_schedule, shifts)
        
        self.setCentralWidget(widget)

w = MainWindow()
w.show()

app.exec()