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
    
    def __init__(self, person, start_time, shifts, durations=[], shift_colors=dict(), other_word = "Other"):
        # TODO add scrolling features
        super(ShiftSelector, self).__init__()
        
        self.person = person
        self.start_time = start_time
        self.shifts = shifts
        self.durations = durations
        if "" not in shift_colors:
            shift_colors[""] = "white"
        self.shift_colors = shift_colors
        self.other_word = other_word
        
        self.active = True
        
        # shift dropdown
        shift_box = QComboBox()
        shift_box.addItems(shifts)
        shift_box.addItem(other_word)
        
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
            self.shift_box.setCurrentText(self.other_word) # Magic Word
            self.text_box.setText(shift)
    
    def get_shift(self):
        if self.shift_box.currentText() == self.other_word:
            return self.text_box.currentText()
        else:
            return self.shift_box.currentText()
    
    def shift_changed(self, shift):
        if shift == self.other_word:
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
    def __init__(self, schedule, shifts, shift_colors=dict(), max_width=-1, max_height=-1, bg_color = "#5C4033"):
        super(CentralGrid, self).__init__()
        
        self.schedule = schedule
        self.shifts = shifts
        self.shift_colors = shift_colors
        
        people = list(schedule.columns)
        self.people = people
        self.people_index = 0
        times = list(schedule.index)
        self.times = times
        self.time_index = 0
        
        if max_width > 0:
            self.max_width = min(max_width,len(people))
        else:
            self.max_width = len(people)
            
        if max_height > 0:
            self.max_height = min(max_height,len(times))
        else:
            self.max_height = len(times)
        
        widget_grid = dict()
        name_widgets = dict()
        time_widgets = dict()
        
        # Names at the top
        for i in range(schedule.shape[1]):
            name = people[i]
            name_widget = QLabel(name)
            name_widget.setAlignment(Qt.AlignCenter)
            
            name_widget.setAutoFillBackground(True)
            palette = name_widget.palette()
            palette.setColor(QPalette.Window, QColor("white"))
            name_widget.setPalette(palette)
            
            name_widgets[name] = name_widget
            
            widget_grid[people[i]] = dict() # initialize the interior of the widget storage
        
        # Times at the left
        for i in range(schedule.shape[0]):
            time = schedule.index[i]
            formatted_time = minutes_to_12h(time)
            time_widget = QLabel(formatted_time)
            time_widget.setAlignment(Qt.AlignCenter)
            
            time_widget.setAutoFillBackground(True)
            palette = time_widget.palette()
            palette.setColor(QPalette.Window, QColor("white"))
            time_widget.setPalette(palette)
            
            time_widgets[time] = time_widget
        
        # Dropdowns in the middle
        # TODO encapsulate the layout creation
        for i in range(len(times)):
            time = times[i]
            
            durations = [repr(30+times[k]-time) for k in range(i,len(times))] # this is very scuffed lol
            for j in range(len(people)):
                person = people[j]
                
                widget = ShiftSelector(person, time, shifts, durations, shift_colors=shift_colors)
                widget.set_shift(self.schedule[person][time])
                
                widget.shiftChanged.connect(partial(self.updateSchedule,person,time))
                widget.shiftChanged.connect(lambda x : self.updateCounters())
                widget_grid[person][time] = widget
        
        main_height = self.max_height+1
        main_width = self.max_width+1
        
        # Column shift counters
        colCounters = {p:QLabel("") for p in schedule.columns} # TODO just make the list of people an input to the grid
        for l in colCounters.values():
            l.setAlignment(Qt.AlignCenter)
            
            l.setAutoFillBackground(True)
            palette = l.palette()
            palette.setColor(QPalette.Window, QColor("white"))
            l.setPalette(palette)
        colShift = ShiftSelector(None, None, shifts, [])
        
        colShift.shiftChanged.connect(lambda x : self.updateCounters())
        self.colShift = colShift
        self.colCounters = colCounters
            
        # Row shift counters
        rowCounters = {t:QLabel("") for t in schedule.index} # TODO make the list of times an input as well?
        for l in rowCounters.values():
            l.setAlignment(Qt.AlignCenter)
            
            l.setAutoFillBackground(True)
            palette = l.palette()
            palette.setColor(QPalette.Window, QColor("white"))
            l.setPalette(palette)
        rowShift = ShiftSelector(None, None, shifts, [])
        
        rowShift.shiftChanged.connect(lambda x : self.updateCounters())
        self.rowShift = rowShift
        self.rowCounters = rowCounters
        
        # TEMPORARY: add a "print" button in the top-left
        # Maybe change this to a save button later?
        print_button = QPushButton("Print")
        print_button.pressed.connect(self.printSchedule)
        self.print_button = print_button
        
        dpad = DPad()
        dpad.directionPushed.connect(self.scroll)
        
        self.widget_grid = widget_grid
        self.name_widgets = name_widgets
        self.time_widgets = time_widgets
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(bg_color))
        self.setPalette(palette)
        
        self.updateLayout(people[:self.max_width],times[:self.max_height])
        self.updateCounters()
    
    def updateSchedule(self, person, time, shift):
        self.schedule[person][time] = shift
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
    
    def updateLayout(self, people=None, times=None):
        if people == None:
            people = self.people[self.people_index:self.people_index+max_width]
        if times == None:
            times = self.times[self.time_index:self.time_index+max_width]
        
        newLayout = QGridLayout()
        main_width = len(people)
        main_height = len(times)
        
        newLayout.addWidget(self.print_button,0,0)
        newLayout.addWidget(self.rowShift,0,main_width+1)
        newLayout.addWidget(self.colShift,main_height+1,0)
        for i in range(len(times)):
            newLayout.addWidget(self.time_widgets[times[i]],i+1,0)
            newLayout.addWidget(self.rowCounters[times[i]],i+1,main_width+1)
        for i in range(len(people)):
            newLayout.addWidget(self.name_widgets[people[i]],0,i+1)
            newLayout.addWidget(self.colCounters[people[i]],main_height+1,i+1)
        
        for i in range(len(times)):
            for j in range(len(people)):
                newLayout.addWidget(self.widget_grid[people[j]][times[i]],i+1,j+1)
                
        if self.people_index+self.max_width < len(self.people):
            pass # TODO add an arrow
        
        newLayout.setSpacing(5)
        # self.layout_dp[(people,times)] = newLayout # does this even work???
        if self.layout():
            QWidget().setLayout(self.layout()) 
            # apparently this basically deletes the old layout as long as we dont keep the reference to it
            # thanks python garbage collection!
        self.setLayout(newLayout)
    
    def scroll(self, direction):
        pass
    
    def printSchedule(self):
        print(self.schedule)