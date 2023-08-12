import pandas as pd
import numpy as np
from functools import partial

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget, QComboBox, QLabel, QPushButton, QLineEdit
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QToolBar, QAction, QStatusBar
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, pyqtSignal

from helpers import *

class ShiftSelector(QWidget):
    shiftChanged = pyqtSignal(str)
    # textboxChanged = pyqtSignal(str)
    durationChanged = pyqtSignal(str)
    
    def __init__(self, person, start_time, shifts, durations, shift_colors=dict(), max_width = 5):
        super(ShiftSelector, self).__init__()
        
        self.person = person
        self.start_time = start_time
        self.shifts = shifts
        self.durations = durations
        self.shift_colors = shift_colors
        if "" not in shift_colors:
            shift_colors[""] = "white"
        
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
        palette.setColor(QPalette.Window, QColor("white")) # Magic Word
        self.setPalette(palette)
    
    # TODO: add color changing to shift_changed/textbox_changed 
    
    def set_shift(self,shift):
        if shift in self.shifts:
            self.shift_box.setCurrentText(shift)
        else:
            self.shift_box.setCurrentText("Other") # Magic Word
            self.text_box.setText(shift)
    
    def get_shift(self):
        if self.shift_box.currentText() == "Other":
            return self.text_box.currentText()
        else:
            return self.shift_box.currentText()
    
    def shift_changed(self, shift):
        if shift == "Other":
            self.text_box.setEnabled(True)
            self.text_box.setVisible(True)
        else:
            self.text_box.setEnabled(False)
            self.text_box.setVisible(False)
            self.shiftChanged.emit(shift)
        
        self.change_color_by_shift(shift)
            
    def textbox_changed(self, text):
        self.shiftChanged.emit(text)
        self.change_color_by_shift(text)
    
    def duration_changed(self, duration):
        self.durationChanged.emit(duration)
    
    def change_color_by_shift(self, shift):
        color = QColor(self.shift_colors[""])
        if shift in self.shift_colors:
            color = QColor(self.shift_colors[shift])
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)

class CentralGrid(QWidget):
    def __init__(self, schedule, shifts, shift_colors=dict()):
        super(CentralGrid, self).__init__()
        
        self.schedule = schedule
        self.shifts = shifts
        self.shift_colors = shift_colors
        
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
                
                widget = ShiftSelector(person, time, shifts, durations, shift_colors=shift_colors)
                widget.set_shift(self.schedule[person][time])
                
                widget.shiftChanged.connect(partial(self.updateSchedule,schedule.columns[j],schedule.index[i]))
                widget.shiftChanged.connect(lambda x : self.updateCounters())
                layout.addWidget(widget, i+1, j+1)
                widget_grid[person][time] = widget
        
        main_height = schedule.shape[0]+1
        main_width = schedule.shape[1]+1
        
        # Column shift counters
        colCounters = {p:QLabel("") for p in schedule.columns} # TODO just make the list of people an input to the grid
        for l in colCounters.values():
            l.setAutoFillBackground(True)
            palette = l.palette()
            palette.setColor(QPalette.Window, QColor("white"))
            l.setPalette(palette)
        colShift = ShiftSelector(None, None, shifts, [])
        # colShift.shiftChanged.connect(updateCounters)
        layout.addWidget(colShift, main_height, 0)
        for i in range(schedule.shape[1]):
            layout.addWidget(colCounters[schedule.columns[i]],main_height,i+1)
        
        colShift.shiftChanged.connect(lambda x : self.updateCounters())
        self.colShift = colShift
        self.colCounters = colCounters
            
        # Row shift counters
        rowCounters = {t:QLabel("") for t in schedule.index} # TODO make the list of times an input as well?
        for l in rowCounters.values():
            l.setAutoFillBackground(True)
            palette = l.palette()
            palette.setColor(QPalette.Window, QColor("white"))
            l.setPalette(palette)
        rowShift = ShiftSelector(None, None, shifts, [])
        # colShift.shiftChanged.connect(updateCounters)
        layout.addWidget(rowShift, 0, main_width)
        for i in range(schedule.shape[0]):
            layout.addWidget(rowCounters[schedule.index[i]],i+1,main_width)
        
        rowShift.shiftChanged.connect(lambda x : self.updateCounters())
        self.rowShift = rowShift
        self.rowCounters = rowCounters
        
        # TEMPORARY: add a "print" button in the top-left
        # Maybe change this to a save button later?
        widget = QPushButton("Print")
        widget.pressed.connect(self.printSchedule)
        layout.addWidget(widget, 0, 0)
        
        layout.setSpacing(5)
        
        self.layout = layout
        self.widget_grid = widget_grid
        self.setLayout(layout)
        
        self.updateCounters()
    
    def updateSchedule(self, person, time, shift):
        self.schedule[person][time] = shift
        # TODO update counters here as well
        # TODO add something about durations?
        
    def updateCounters(self):
        colShift = self.colShift.get_shift()
        for p in self.colCounters:
            val_counts = self.schedule[p].value_counts()
            if colShift in val_counts:
                self.colCounters[p].setText(repr(val_counts[colShift]))
            else:
                self.colCounters[p].setText("0")
        
        rowShift = self.rowShift.get_shift()
        for t in self.rowCounters:
            val_counts = self.schedule.loc[t].value_counts()
            if rowShift in val_counts:
                self.rowCounters[t].setText(repr(val_counts[rowShift]))
            else:
                self.rowCounters[t].setText("0")
        
    def printSchedule(self):
        print(self.schedule)