import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import mytools

class ControlGeneralFrame(tk.Frame):
    STOP = "stop"
    SETZERO = "setzero"
    GOZERO = "gozero"

    def __init__(self, master, axis_names, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.btnStop    = tk.Button(self, text="STOP Movements",command=self.stop)
        self.btnSetZero = tk.Button(self, text="Set as Zero",   command=self.setZero)
        self.btnGoZero  = tk.Button(self, text="Go to Zero",    command=self.goZero)

        self.btnStop.config(
            height=1, 
            font=("Arial",13), 
            bg="#E70606", 
            fg="#FFFFFF", 
            relief="solid", 
            borderwidth=2,
            activebackground="#B50000",
            activeforeground="#DDDDDD")
        self.btnSetZero.config(
            height=1, 
            font=("Arial",12), 
            bg="#C06C55", 
            fg="#FFFFFF", 
            relief="flat",
            activebackground="#964D39",
            activeforeground="#DDDDDD")
        self.btnGoZero.config(
            height=1, 
            font=("Arial",12), 
            bg="#CBB46A", 
            fg="#FFFFFF", 
            relief="flat",
            activebackground="#A89249",
            activeforeground="#DDDDDD")

        self.lblNames = [ tk.Label(self, text=axis_name) for axis_name in axis_names ]
        self.inpAxisValues = { axis_name:tk.DoubleVar() for axis_name in axis_names }
        self.lblAxisValues = [ tk.Label(self, textvariable=inpAxis, bg="#B5D6C1", anchor="w") for inpAxis in self.inpAxisValues.values() ]

        self.callbacks = {
            "stop": [],
            "setzero": [],
            "gozero": []
        }

        self.apply_layout()

    def addCallback(self, target: str, callback):
        self.callbacks[target].append(callback)

    def stop(self):
        # apply pressed layout
        # call callbacks
        for cb in self.callbacks[self.STOP]: cb()
        # maybe return to normal
    
    def setZero(self):
        # call callbacks
        for cb in self.callbacks[self.SETZERO]: cb()

    def goZero(self):
        # apply pressed layout
        # call callbacks
        for cb in self.callbacks[self.GOZERO]: cb()
        # maybe return to normal

    def apply_layout(self):
        self.pack(fill="x")
        self.rowconfigure(tuple(range(len(self.lblNames)+3)), weight=3, uniform='a')
        self.rowconfigure((0), weight=4, uniform='a')
        self.columnconfigure((0), weight=1, uniform='a')
        self.columnconfigure((1), weight=3, uniform='a')

        self.btnStop.   grid(row=0, column=0, columnspan=2, sticky="nsew", pady=2)
        self.btnSetZero.grid(row=4, column=0, columnspan=2, sticky="ew", pady=2)
        self.btnGoZero. grid(row=5, column=0, columnspan=2, sticky="ew", pady=2)
        
        for idxAxis in range(len(self.lblNames)):
            self.lblNames[idxAxis].     grid(row=idxAxis+1, column=0, sticky="ew")
            self.lblAxisValues[idxAxis].grid(row=idxAxis+1, column=1, sticky="ew", padx=10)

    def reset_layout(self):
        self.pack_forget()
        self.grid_forget()

        for child in self.winfo_children():
            child.pack_forget()
            child.grid_forget()


def testControlGeneralFrame():
    print("start testControlGeneralFrame")
    root = tk.Tk()

    cgf = ControlGeneralFrame(root, ('X','Y','Z'))

    root.mainloop()

if __name__ == "__main__":
    print("start")

    testControlGeneralFrame()