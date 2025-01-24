import tkinter as tk
from tkinter import StringVar
from tkinter import ttk
import json
import config

class ModelSettings:
    """
    Summary
        ----------
        Load settings data from a file.

    Property
        ----------
        INIT_UNIT : str
            Inital unit value from a settings file for the distance movements in metric system.
        INIT_PORT : str
            Inital port value from a settings file for the connexion with controller.
        INIT_BAUDRATE : int
            Inital unit value from a settings file to calibrate the baud rate with the controller in baud/sec.
        INIT_STEPRATE : int
            Inital unit value from a settings file to calibrate the step/distance ratio in step/unit.
        unit : str
            Distance movements in metric system.
        port : str
            Port for the connexion with the controller
        baudrate : int
            Calibrate the baud rate with the controller in baud/sec.
        steprate : int
            Calibrate the step/distance ratio in step/unit

    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.load(filepath)
        self.reset()

    def load(self, filepath=None):
        if filepath is None:
            filepath = self.filepath
        with open(filepath,'r') as settingsFile:
            settings = json.load(settingsFile)
        self.INIT_UNIT = settings["settings"]["unit"]
        self.INIT_PORT = settings["settings"]["port"]
        self.INIT_BAUDRATE = settings["settings"]["baudrate"]
        self.INIT_STEPRATE = settings["settings"]["steprate"]
    
    def reset(self):
        self.unit = self.INIT_UNIT
        self.port = self.INIT_PORT
        self.baudrate = self.INIT_BAUDRATE
        self.steprate = self.INIT_STEPRATE

class PresenterSettings(tk.Frame):
    """

    Summary
        ----------
        Frame that create it's component and manage inputs.
        Use ModeleSettings and ViewSettings.
        Used to access settings and temporary change them.

    """
    def __init__(self, master, model=None, filepath=None):
        super().__init__(master)
        self.root = master.nametowidget(".")

        if(model):
            self.model = model
        elif(filepath):
            self.model = ModelSettings(filepath=filepath)
        else:
            print("No model or filepath given in parameter")
            raise TypeError
            

        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.master = master

        # Panels
        self.pnlSettings    = tk.PanedWindow(self)
        self.pnlButtons     = tk.PanedWindow(self)
        self.pnlCurrentVal  = tk.PanedWindow(self)

        # Components
        self.title = tk.Label(self, text="Settings")

        self.lblUnit    = tk.Label(self.pnlSettings, text="Unit")
        self.inpUnit    = tk.StringVar()
        self.entUnit    = tk.Entry(self.pnlSettings, textvariable=self.inpUnit)

        self.lblPort    = tk.Label(self.pnlSettings, text="Port")
        self.inpPort    = tk.StringVar()
        self.entPort    = tk.Entry(self.pnlSettings, textvariable=self.inpPort)

        self.lblBaudrate= tk.Label(self.pnlSettings, text="Baud rate")
        self.inpBaudrate= tk.StringVar()
        self.entBaudrate= tk.Entry(self.pnlSettings, textvariable=self.inpBaudrate)

        self.lblSteprate= tk.Label(self.pnlSettings, text="Step rate")
        self.inpSteprate= tk.StringVar()
        self.entSteprate= tk.Entry(self.pnlSettings, textvariable=self.inpSteprate)

        self.btnApply   = tk.Button(self.pnlButtons, text="Apply",  command=self.apply)
        self.btnCancel  = tk.Button(self.pnlButtons, text="Cancel", command=self.cancel)
        self.btnReset   = tk.Button(self.pnlButtons, text="Reset",  command=self.reset)

        self.lblValUnit     = tk.Label(self.pnlCurrentVal)
        self.lblValPort     = tk.Label(self.pnlCurrentVal)
        self.lblValBaudrate    = tk.Label(self.pnlCurrentVal)
        self.lblValSteprate = tk.Label(self.pnlCurrentVal)

        self.view = ViewSettings(self)
        self.refresh()
        self.cancel()

    def _close(self):
        self.root.quit()
        self.root.destroy()

    def refresh(self):
        self.lblValUnit.config(text=self.model.unit)
        self.lblValPort.config(text=self.model.port)
        self.lblValBaudrate.config(text=self.model.baudrate)
        self.lblValSteprate.config(text=self.model.baudrate)

    def apply(self):
        print("apply current settings")
        self.model.unit = self.inpUnit.get()
        self.model.port = self.inpPort.get()
        self.model.baudrate = int(self.inpBaudrate.get())
        self.model.steprate = int(self.inpSteprate.get())
        self.refresh()

    def cancel(self):
        print("cancel current settings")
        self.inpUnit.set(self.model.unit)
        self.inpPort.set(self.model.port)
        self.inpBaudrate.set(str(self.model.baudrate))
        self.inpSteprate.set(str(self.model.steprate))

    def reset(self):
        print("reset current settings")
        self.model.reset()
        self.cancel()
        self.refresh()

class ViewSettings:
    """
    Summary
        ----------
        Manage widget placement and aesthetic of a PresenterSettings
    """
    def __init__(self, presenter):
        self.presenter = presenter
        
        # Frame
        self.presenter.columnconfigure((0), weight=1, uniform='a')
        self.presenter.rowconfigure((1,2,3,4,5,6), weight=1, uniform='a')
        self.presenter.pack(expand=True, fill="both")

        # Panels
        self.presenter.pnlSettings.config(orient=tk.VERTICAL)
        self.presenter.pnlSettings.grid(row=1, column=0, rowspan=4,sticky="nsew")
        self.presenter.pnlSettings.rowconfigure((0,1,2,3), weight=1, uniform='a')
        self.presenter.pnlSettings.columnconfigure((0,1,2), weight=1, uniform='a')

        self.presenter.pnlButtons.config(orient=tk.HORIZONTAL)
        self.presenter.pnlButtons.grid(row=5, column=0, sticky="nsew")
        self.presenter.pnlButtons.rowconfigure(0, weight=1)
        self.presenter.pnlButtons.columnconfigure((0,1,2), weight=1)

        self.presenter.pnlCurrentVal.config(orient=tk.HORIZONTAL)
        self.presenter.pnlCurrentVal.grid(row=6,column=0, sticky="nsew")
        self.presenter.pnlCurrentVal.rowconfigure(0, weight=1)
        self.presenter.pnlCurrentVal.columnconfigure((0,1,2,3), weight=1)

        # Components
        self.presenter.title.grid(row=0,column=0)

        self.presenter.lblUnit      .grid(row=0,column=0)
        self.presenter.entUnit      .grid(row=0,column=1, sticky="nsew", padx=5, pady=2)
        self.presenter.entUnit      .config(width=10)

        self.presenter.lblPort      .grid(row=1,column=0)
        self.presenter.entPort      .grid(row=1,column=1, sticky="nsew", padx=5, pady=2)
        self.presenter.entPort      .config(width=10)

        self.presenter.lblBaudrate  .grid(row=2,column=0)
        self.presenter.entBaudrate  .grid(row=2,column=1, sticky="nsew", padx=5, pady=2)
        self.presenter.entBaudrate  .config(width=10)

        self.presenter.lblSteprate  .grid(row=3,column=0)
        self.presenter.entSteprate  .grid(row=3,column=1, sticky="nsew", padx=5, pady=2)
        self.presenter.entSteprate  .config(width=10)

        self.presenter.btnApply     .grid(row=0, column=0, sticky="nsew",padx=3)
        self.presenter.btnCancel    .grid(row=0, column=1, sticky="nsew",padx=3)
        self.presenter.btnReset     .grid(row=0, column=2, sticky="nsew",padx=3)
        self.presenter.btnApply     .config(bg="#A5EF91", activebackground="#ccffcc", relief=tk.FLAT, width=10, height=2)
        self.presenter.btnCancel    .config(bg="#EFED91", activebackground="#fffea3", relief=tk.FLAT, width=10, height=2)
        self.presenter.btnReset     .config(bg="#F15A5A", activebackground="#ffcccc", relief=tk.FLAT, width=10, height=2)

        self.presenter.lblValUnit       .grid(row=0,column=0,sticky="nsew",ipadx=5,padx=10)
        self.presenter.lblValPort       .grid(row=0,column=1,sticky="nsew",ipadx=5,padx=10)
        self.presenter.lblValBaudrate   .grid(row=0,column=2,sticky="nsew",ipadx=5,padx=10)
        self.presenter.lblValSteprate   .grid(row=0,column=3,sticky="nsew",ipadx=5,padx=10)
        self.presenter.lblValUnit       .config(bg="#aaaaaa")
        self.presenter.lblValPort       .config(bg="#aaaaaa")
        self.presenter.lblValBaudrate   .config(bg="#aaaaaa")
        self.presenter.lblValSteprate   .config(bg="#aaaaaa")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Testing Settings frame")
    root.geometry("500x220")

    model = ModelSettings(config.path+"settings.json")
    app = PresenterSettings(root, model=model)
    
    root.mainloop()

    # testJson()