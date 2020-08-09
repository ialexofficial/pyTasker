from widgets import *
from tkinter import Tk, mainloop

tasks = {}

root = Tk()
TaskContainer(tasks, root)

if __name__ == '__main__':
    mainloop()