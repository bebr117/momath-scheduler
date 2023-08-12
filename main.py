import pandas as pd

from PyQt5.QtWidgets import QMainWindow, QApplication

from scheduling_grid import CentralGrid
from helpers import *

app = QApplication([])

shifts=["None","Float","0","-1","Security","Greet","Tickets","Lunch","Coro","Trike","Gallery"]
people=["Brian","Ross","Will"]
shift_colors={
    "":"white",
    "0":"red",
    "-1":"yellow",
    "Security":"blue",
    "Greet":"magenta",
    "Lunch":"gray",
    "Gallery":"green",
    "Coro":"#F5F5DC",
    "Trike":"cyan"
}

start_time = 600
end_time = 1020
default_schedule = pd.DataFrame("Float", index=range(start_time,end_time,30),columns=people)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.setWindowTitle("MoMath Schedule Manager")
        
        widget = CentralGrid(default_schedule, shifts, shift_colors)
        
        self.setCentralWidget(widget)
        # TODO change default margins

w = MainWindow()
w.show()

app.exec()