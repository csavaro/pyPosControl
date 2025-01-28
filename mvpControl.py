import tkinter as tk
from tkinter import StringVar
from tkinter import ttk
from mvpSettings import ModelSettings,PresenterSettings
import config

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
    def __init__(self, master, modelSettings, modelControl=None):
        super().__init__(master)
        self.root = master.nametowidget(".")

        self.modelSettings = modelSettings
        if(modelControl):
            self.model = modelControl
        else:
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
        self.inpX       = tk.StringVar(value=0)
        self.inpX.trace_add("write", lambda name, index, mode, sv=self.inpX: self.changeX())
        self.entX       = tk.Spinbox(self.pnlManual, textvariable=self.inpX, from_=-8000000, to=8000000)

        # Better with logo instead
        self.lblY       = tk.Label(self.pnlManual, text="Y")
        self.lblYunit   = tk.Label(self.pnlManual, text=self.modelSettings.unit)
        self.inpY       = tk.StringVar(value=0)
        self.inpY.trace_add("write", lambda name, index, mode, sv=self.inpY: self.changeY())
        self.entY       = tk.Spinbox(self.pnlManual, textvariable=self.inpY, from_=-8000000, to=8000000)
        # self.entY.config(validate="all", validatecommand=)

        # Better with logo instead
        self.btnReset   = tk.Button(self.pnlManual, text="Reset", command=self.reset)
        
        self.mappingButtons = {
            "btnUp"     : self.incrY,
            "btnDown"   : self.decrY,
            "btnRight"  : self.incrX,
            "btnLeft"   : self.decrX
        }

        # Better with logos instead
        self.btnUp      = tk.Button(self.pnlButtons, text="Up",     command=lambda: self.pressButton("btnUp"))
        self.btnDown    = tk.Button(self.pnlButtons, text="Down",   command=lambda: self.pressButton("btnDown"))
        self.btnRight   = tk.Button(self.pnlButtons, text="Right",  command=lambda: self.pressButton("btnRight"))
        self.btnLeft    = tk.Button(self.pnlButtons, text="Left",   command=lambda: self.pressButton("btnLeft"))
        
        self.btnReverseX = tk.Button(self.pnlReverse, text="Reverse X axis", command=self.reverseX)
        self.btnReverseY = tk.Button(self.pnlReverse, text="Reverse Y axis", command=self.reverseY)

        # Interface
        self.view = ViewControl(self)
        self.refreshXY()

    def _close(self):
        self.root.quit()
        self.root.destroy()

    def refreshXY(self):
        print("refresh xy")
        self.inpX.set(self.model.x_move)
        self.inpY.set(self.model.y_move)

    def reset(self):
        print("reset")
        self.model.reset()
        self.refreshXY()

    def pressButton(self, name, event=None):
        self.mappingButtons[name]()
        self.refreshXY()

    def changeX(self):
        if self.inpX.get():
            print(f"found x = {float(self.inpX.get())}")
            self.model.x_move = float(self.inpX.get())

    def changeY(self):
        if self.inpY.get():
            print(f"found y = {float(self.inpY.get())}")
            self.model.y_move = float(self.inpY.get())

    def incrY(self):
        if(self.root.focus_get() not in (self.entY,self.entX)):
            print("incr y")
            self.model.y_move += 1

    def decrY(self):
        if(self.root.focus_get() not in (self.entY,self.entX)):
            print("decr y")
            self.model.y_move -= 1

    def incrX(self):
        if(self.root.focus_get() not in (self.entY,self.entX)):
            print("incr x")
            self.model.x_move += 1
        pass

    def decrX(self):
        if(self.root.focus_get() not in (self.entY,self.entX)):
            print("decr x")
            self.model.x_move -= 1
        pass

    def reverseX(self):
        print("reverse x")
        self.mappingButtons["btnLeft"],self.mappingButtons["btnRight"] = self.mappingButtons["btnRight"],self.mappingButtons["btnLeft"]
        self.model.reverseX()
        self.refreshXY()

    def reverseY(self):
        print("reverse y")
        self.mappingButtons["btnUp"],self.mappingButtons["btnDown"] = self.mappingButtons["btnDown"],self.mappingButtons["btnUp"]
        self.model.reverseY()
        self.refreshXY()

class ViewControl:
    """

    Summary
        ----------
        Manage widget placement and aesthetic of a PresenterControl

    """
    def __init__(self, presenter):
        # Maybe remove when finished
        nf = True
        if nf:
            self.presenter = presenter
        else:
            # For auto-completion
            self.presenter = PresenterControl()

        # Frame
        self.presenter.columnconfigure((0), weight=1, uniform='a')
        self.presenter.rowconfigure((1), weight=1, uniform='a')
        self.presenter.rowconfigure((2), weight=3, uniform='a')
        self.presenter.rowconfigure((0,3), weight=1, uniform='a')
        self.presenter.pack(expand=True, fill="both")        

        # Panels
        # self.presenter.pnlManual.config(bg="#FFDDDD")
        self.presenter.pnlManual.grid(row=1,column=0, sticky="nsew")
        self.presenter.pnlManual.rowconfigure((0,1), weight=1, uniform='a')
        self.presenter.pnlManual.columnconfigure((0,2,3), weight=1, uniform='a')
        self.presenter.pnlManual.columnconfigure((1), weight=2, uniform='a')

        # self.presenter.pnlButtons.config(bg="#DDFFDD")
        self.presenter.pnlButtons.grid(row=2,column=0, sticky="nsew")
        self.presenter.pnlButtons.rowconfigure((0,1,2), weight=1, uniform='a')
        self.presenter.pnlButtons.columnconfigure((0,1,2), weight=1, uniform='a')

        self.presenter.pnlReverse.config(orient=tk.HORIZONTAL)
        self.presenter.pnlReverse.grid(row=3,column=0, sticky="sew")
        self.presenter.pnlReverse.rowconfigure(0, weight=1, uniform='a')
        self.presenter.pnlReverse.columnconfigure((0,1), weight=1, uniform='a')

        # Components
        self.presenter.title.grid(row=0,column=0)

        # Manual
        self.presenter.lblX     .grid(row=0, column=0, sticky="nse")
        self.presenter.lblXunit .grid(row=0, column=2, sticky="nsw")
        self.presenter.entX     .grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.presenter.entX     .config(width=10)

        self.presenter.lblY     .grid(row=1, column=0, sticky="nse")
        self.presenter.lblYunit .grid(row=1, column=2, sticky="nsw")
        self.presenter.entY     .grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.presenter.entY     .config(width=10)

        self.presenter.btnReset .grid(row=0, column=3, rowspan=2, sticky="nsew", padx=3, pady=3)
        self.presenter.btnReset .config(bg="#EFED91", activebackground="#DFDD81", relief=tk.FLAT, width=5, height=5)

        # Buttons
        self.presenter.btnUp    .grid(row=0, column=1, sticky="nsew")
        self.presenter.btnDown  .grid(row=2, column=1, sticky="nsew")
        self.presenter.btnRight .grid(row=1, column=2, sticky="nsew")
        self.presenter.btnLeft  .grid(row=1, column=0, sticky="nsew")
        self.presenter.btnUp    .config(bg="#D9D9D9", activebackground="#C9C9C9", relief=tk.FLAT, width=10, height=5)
        self.presenter.btnDown  .config(bg="#D9D9D9", activebackground="#C9C9C9", relief=tk.FLAT, width=10, height=5)
        self.presenter.btnRight .config(bg="#D9D9D9", activebackground="#C9C9C9", relief=tk.FLAT, width=10, height=5)
        self.presenter.btnLeft  .config(bg="#D9D9D9", activebackground="#C9C9C9", relief=tk.FLAT, width=10, height=5)
        
        # Reverse
        self.presenter.btnReverseX.grid(row=0, column=0, sticky="nsew", padx=3)
        self.presenter.btnReverseY.grid(row=0, column=1, sticky="nsew", padx=3)
        self.presenter.btnReverseX.config(bg="#F15A5A", fg="#FFFFFF", activebackground="#E14A4A", relief=tk.SOLID, bd=1)
        self.presenter.btnReverseY.config(bg="#71C257", fg="#FFFFFF", activebackground="#61B247", relief=tk.SOLID, bd=1)

def ma(lo):
    print("a")
    print(lo)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Testing Control frame")
    root.geometry("500x500")
    
    mSettings = ModelSettings(config.path+"settings.json")
    mControl = ModelControl(steprate=mSettings.steprate)

    app = PresenterControl(root,modelSettings=mSettings, modelControl=mControl)

    # sett = PresenterSettings(root, config.path+"settings.json")
    # app = PresenterControl(root, sett.model)

    # Shortcuts
    root.bind("<Up>",   lambda event, name="btnUp":     app.pressButton(name, event))
    root.bind("<Down>", lambda event, name="btnDown":   app.pressButton(name, event))
    root.bind("<Right>",lambda event, name="btnRight":  app.pressButton(name, event))
    root.bind("<Left>", lambda event, name="btnLeft":   app.pressButton(name, event))

    root.mainloop()