import tkinter as tk
from tkinter import StringVar
from tkinter import ttk
from mvpSettings import ModelSettings

class ModelControl:
    """

    Summary
        ----------
        Save x and y movement distance.
        Execute/Send the movements on the controller

    Property
        ----------
        x_move : int
            Movement on X axis prepared in steps.
        y_move : int
            Movement on Y axis prepared in steps.
        x_speed : int
            Speed of movements on X axis in step/sec.
        y_speed : int
            Speed of movements on Y axis in step/sec.
        steprate : int
            Ratio for conversion step to metric system in step/mm.
        
    """
    def __init__(self, x_speed=0, y_speed=0, steprate=0):
        self.reset()
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.steprate = steprate

    def reset(self):
        self.x_move = 0
        self.y_move = 0

    def reverseX(self):
        self.x_move = -self.x_move
    
    def reverseY(self):
        self.y_move = -self.y_move

    def setX(self, value):
        # Convert from it's unit to mm
        pass

    def setY(self, value):
        # Convert from it's unit to mm
        pass

    def getCommand(self):
        cmd = f"@0a{self.x_move},{self.x_speed},{self.y_move},{self.y_speed}"
        print(cmd)
        return bytes(cmd,'ascii')
    
if __name__ == "__main__":
    print("start mvpControl")

    m = ModelControl(500,500,100)
    print(m.getCommand())

    print("end mvpControl")

class PresenterControl(tk.Frame):
    """

    Summary
        ----------
        Frame that create it's component and manage inputs.
        Use ModelControl and ViewControl.
        Used to control a robot on X and Y axis by manual values and/or buttons.

    """
    def __init__(self, master, modelSettings):
        super().__init__(master)
        self.root = master.nametowidget(".")

        self.modelSettings = modelSettings
        # Find a way to init its params
        self.model = ModelControl(steprate=modelSettings.steprate)

        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.master = master

        # Panels
        self.pnlManual  = tk.PanedWindow(self)
        self.pnlButtons = tk.PanedWindow(self)
        self.pnlReverse = tk.PanedWindow(self)

        # Components
        self.title = tk.Label(self, text="Control")

        # Better with logo instead
        self.lblX       = tk.Label(self.pnlManual, text="X")
        self.lblXunit   = tk.Label(self.pnlManual, text=self.modelSettings.unit)
        self.inpX       = tk.StringVar()
        self.entX       = tk.Spinbox(self.pnlManual, textvariable=self.inpX, from_=-8000000, to=8000000)

        # Better with logo instead
        self.lblY       = tk.Label(self.pnlManual, text="Y")
        self.lblXunit   = tk.Label(self.pnlManual, text=self.modelSettings.unit)
        self.inpY       = tk.StringVar()
        self.entY       = tk.Spinbox(self.pnlManual, textvariable=self.inpY, from_=-8000000, to=8000000)

        # Better with logo instead
        self.btnReset   = tk.Button(self.pnlManual, text="Reset", command=self.reset)
        
        self.btnMapping = {
            "btnUp"     : self.incrY,
            "btnDown"   : self.decrY,
            "btnRight"  : self.incrX,
            "btnLeft"   : self.decrX
        }

        # Better with logos instead
        self.btnUp      = tk.Button(self.pnlButtons, text="Up",     command=self.btnMapping["btnUp"])
        self.btnDown    = tk.Button(self.pnlButtons, text="Down",   command=self.btnMapping["btnDown"])
        self.btnRight   = tk.Button(self.pnlButtons, text="Right",  command=self.btnMapping["btnRight"])
        self.btnLeft    = tk.Button(self.pnlButtons, text="Left",   command=self.btnMapping["btnLeft"])
        
        self.btnReverseX = tk.Button(self.pnlReverse, text="Reverse X axis", command=self.reverseX)
        self.btnReverseY = tk.Button(self.pnlReverse, text="Reverse Y axis", command=self.reverseY)

        self.view = ViewControl(self)
        self.refreshXY()

    def refreshXY(self):
        self.inpX.set(self.model.x_move)
        self.inpY.set(self.model.y_move)

    def reset(self):
        self.model.reset()
        self.refreshXY()
    
    def incrY(self):
        pass

    def decrY(self):
        pass

    def incrX(self):
        pass

    def decrX(self):
        pass

    def reverseX(self):
        self.btnMapping["btnLeft"],self.btnMapping["btnRight"] = self.btnMapping["btnRight"],self.btnMapping["btnLeft"]
        self.model.reverseX()

    def reverseY(self):
        self.btnMapping["btnUp"],self.btnMapping["btnDown"] = self.btnMapping["btnDown"],self.btnMapping["btnUp"]
        self.model.reverseY()

class ViewControl:
    """

    Summary
        ----------
        Manage widget placement and aesthetic of a PresenterControl

    """
    def __init__(self, presenter):
        self.presenter = presenter

        # Frame

        # Panels

        # Components
