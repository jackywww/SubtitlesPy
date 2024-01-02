import tkinter

class Activate():
    def __init__(self):
        self.root = tkinter.Tk(className="概")

    def position(self, width, height, x, y):
        self.root.geometry("%dx%d+%d+%d" % width, height, x, height)