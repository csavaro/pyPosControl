import tkinter as tk
from tkinter import ttk,DoubleVar
from tkinter.font import Font
import config

# Custom widgets for the two axis control app

class AxisLabeledEntry:
    """
    Summary:
        Bunch of tkinter widgets for axis.
        Used in AxisFrame class.
    Attributes:
        - lblAxis: label, title of the axis.
        - spbAxis: spinbox, input of the axis value.
        - inpAxis: doublevar, value from the input spbAxis.
        - lblUnit (optional): label, additional info like unit of the axis value.
    """
    def __init__(self,master: tk.Widget,label: str,unit: str = None):
        self.lblAxis = tk.Label(master, text=label)
        self.inpAxis = DoubleVar(value=0.0)
        self.spbAxis = tk.Spinbox(master, textvariable=self.inpAxis, from_=-8000000, to=8000000, width=20)
        if unit:
            self.lblUnit = tk.Label(master, text=unit)

class AxisFrame(tk.Frame):
    """
    Summary:
        Tkinter frame with axis value inputs.
        Create necessary widgets and apply them a layout for their positions.
        Additional button to reset inputs.
    Attributes:
        - axis: list, list of AxisLabeledEntry to have an input for each axis (label,input,unit).
        - btnReset: button, reset all axis inputs.
    """
    def __init__(self,master: tk.Widget,axis_names = None, *args, **kwargs):
        super().__init__(master,*args,**kwargs)
        
        if not axis_names:
            axis_names = ('X','Y','Z')
        self.axis = [ AxisLabeledEntry(self,axis_name,"mm") for axis_name in axis_names ]

        self.btnReset = tk.Button(self, text="Reset", bg="#EFED91", relief=tk.GROOVE, command=self.reset_values)

        self.apply_layout()

    def reset_values(self):
        for oneAxis in self.axis:
            oneAxis.inpAxis.set(0)
        
    def apply_layout(self):
        self.pack(fill="x")
        self.columnconfigure((0,2,3), weight=1, uniform='a')
        self.columnconfigure((1), weight=2, uniform='a')
        self.rowconfigure(tuple(range(len(self.axis))), weight=1, uniform='a')

        for idxAxis in range(len(self.axis)):
            self.axis[idxAxis].lblAxis.grid(column=0, row=idxAxis)
            self.axis[idxAxis].spbAxis.grid(column=1, row=idxAxis, sticky="ew")
            self.axis[idxAxis].spbAxis.config(from_=0)
            if self.axis[idxAxis].lblUnit:
                self.axis[idxAxis].lblUnit.grid(column=2, row=idxAxis)
        self.btnReset.grid(column=3, row=0, rowspan=len(self.axis), sticky="nsew")

    def reset_layout(self):
        self.grid_forget()
        self.pack_forget()

        for widget in self.winfo_children():
            widget.grid_forget()
            widget.pack_forget()

class SettingLabeledEntry:
    """
    Summary:
        Bunch of tkinter widgets with their operations between them.
        Used in SettingsFrame class.
    Attributes:
        - options (optional): dict, different preset values displayed by names in a combobox.
        - lblSetting: label, title of the setting.
        - entValue: entry, input/display of the setting value. Disabeled if there is a cmbSetting.
        - inpValue: stringvar, value of the input/display entValue.
        - cmbSetting (optional): combobox, input of preset setting values by names from options.
            When option selected, set it's value in inpValue to be displayed in entValue.
        - lblUnit (optional): label, unit of the setting value.
    """
    def __init__(self, master: tk.Widget, label: str, options: dict, unit: str = None):
        # ! TO CLEANUP !
        # Example
        ex_options = {
            "platine1": {
                "name": "Platine 1",
                "value": 100
            },
            "platine2": {
                "name": "Platine 2",
                "value": 200
            }
        }
        self.options = options

        # Create widgets
        self.lblSetting = tk.Label(master, text=label)
        self.inpValue = tk.StringVar()
        self.entValue = tk.Entry(master, textvariable=self.inpValue, state="disabled")
        self.cmbSetting = None
        if options:
            self.cmbSetting = ttk.Combobox(master, state="readonly") # values=options maybe
        self.lblUnit = None
        if unit:
            self.lblUnit = tk.Label(master, text=unit, fg="#606060", font=Font(size=10,slant="italic"))

        # Add options to droplist (Combobox)
        if options:
            listOptions = [ oneOption["name"] for oneOption in options.values() ]
            self.cmbSetting.config(values=listOptions)
            self.cmbSetting.bind("<<ComboboxSelected>>", self.applyOption)
        else:
            self.entValue.config(state="normal")
    
    def applyOption(self, event=None):
        target_value = searchByName(self.options, self.cmbSetting.get())["value"]
        self.inpValue.set(target_value)
    
    def setVal(self, value):
        if self.cmbSetting:
            # Select the option if found
            if value in self.options.keys():
                self.cmbSetting.set(self.options[value]["name"])
                self.applyOption()
                return
        self.inpValue.set(value)


class SettingsFrame(tk.Frame):
    """
    Summary:
        Tkinter frame of settings options.
    """
    def __init__(self, master: tk.Widget, options: dict, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # ! TO CLEANUP !
        # Example
        ex_options = {
            "parameters": {
                "speed": {
                    "name": "Speed",
                    "unit": "mm",
                    "default": 45
                },
                "stepscaleX": {
                    "name": "Step Scale",
                    "unit": "step/mm",
                    "options": { # from json
                        "platine1": {
                            "name": "Platine 1",
                            "value": 100
                        },
                        "platine2": {
                            "name": "Platine 2",
                            "value": 200
                        }
                    }
                }
            },
            "configs": {
                "config1": {
                    "name": "Config 1",
                    "speed": 60,
                    "stepscaleX": "platine1"
                },
                "config2": {
                    "name": "Config 2",
                    "speed": 75,
                    "stepscaleX": "platine2"
                }
            }
        }

        self.options = options
        # Panels
        self.pnlSettings = tk.PanedWindow(self, orient=tk.VERTICAL)
        self.pnlButtons = tk.PanedWindow(self, orient=tk.HORIZONTAL)

        # Create all settings parameters widgets
        self.parameters = {}
        for key,oneOption in options["parameters"].items():
            optParam = None
            unitParam = None
            # Check if option and unit exist for parameter
            if "options" in oneOption.keys():
                optParam = oneOption["options"]
            if "unit" in oneOption.keys():
                unitParam = oneOption["unit"]
            
            self.parameters.update(
                { 
                    key:
                    SettingLabeledEntry(
                        master=self.pnlSettings,
                        label=oneOption["name"],
                        options= optParam,
                        unit= unitParam
                    )
                }
            )

            if "default" in oneOption.keys():
                self.parameters[key].setVal(oneOption["default"])

        # Create import settings widgets
        self.lblImport = tk.Label(self.pnlSettings, text="Import settings")
        self.cmbImport = ttk.Combobox(self.pnlSettings, state="readonly")
        listOptions = [ oneOption["name"] for oneOption in options["configs"].values() ]
        self.cmbImport.config(values=listOptions)

        # Create buttons widgets
        self.btnApply = tk.Button(self.pnlButtons, text="Apply", command=self.apply, bg="#A5EF91", padx=5, pady=5)
        self.btnCancel = tk.Button(self.pnlButtons, text="Cancel", command=self.cancel, bg="#EFED91", padx=5, pady=5)
        self.btnReset = tk.Button(self.pnlButtons, text="Reset", command=self.reset, bg="#F15A5A", padx=5, pady=5)

        # Listeners
        self.cmbImport.bind("<<ComboboxSelected>>", self.apply_config)
        

        self.applyCallbacks = []
        self.cancelCallbacks = []
        self.resetCallbacks = []

        self.apply_layout()

    def addApplyCallback(self, callback):
        self.applyCallbacks.append(callback)

    def addCancelCallback(self, callback):
        self.cancelCallbacks.append(callback)

    def addResetCallback(self, callback):
        self.resetCallbacks.append(callback)

    def apply_config(self, event=None):
        target_config = searchByName(self.options["configs"],self.cmbImport.get())
        target_OptionKey = list(self.options["configs"].keys())[list(self.options["configs"].values()).index(target_config)]
        for key,val in self.options["configs"][target_OptionKey].items():
            if key in self.parameters.keys():
                self.parameters[key].setVal(val)

    def apply(self):
        for callback in self.applyCallbacks:
            callback()
        # Interface changes
        pass

    def cancel(self):
        for callback in self.cancelCallbacks:
            callback()
        # Interface changes
        pass

    def reset(self):
        for callback in self.resetCallbacks:
            callback()
        # Interface changes
        pass
        # Update
        self.apply()

    def apply_layout(self):
        self.pack(fill="x")
        self.rowconfigure(tuple(range(len(self.parameters)+1)), weight=1, uniform='a')
        self.rowconfigure((len(self.parameters)+2), weight=2, uniform='a')
        self.columnconfigure((0), weight=1, uniform='a')
        
        # Panels
        self.pnlSettings.grid(row=1, column=0, rowspan=len(self.parameters)+1, sticky="ew")
        self.pnlSettings.rowconfigure(tuple(range(len(self.parameters)+1)), weight=1, uniform='a')
        self.pnlSettings.columnconfigure((0,1,3), weight=1, uniform='a')
        self.pnlSettings.columnconfigure((2), weight=2, uniform='a')

        self.pnlButtons.grid(row=len(self.parameters)+2, column=0, sticky="ew")
        self.pnlButtons.rowconfigure((0), weight=1, uniform='a')
        self.pnlButtons.columnconfigure((0,1,2), weight=1, uniform='a')

        # Components
        # Parameters
        idx = 0
        for param in self.parameters.values():
            param.lblSetting.grid(row=idx, column=0, pady=5, padx=10, sticky="w")
            param.entValue.grid(row=idx, column=1, sticky="ew", padx=5)
            if param.cmbSetting:
                param.cmbSetting.grid(row=idx, column=2, sticky="ew", padx=5)
            else:
                param.entValue.grid(row=idx, column=1, columnspan=2, sticky="ew")
            if param.lblUnit:
                param.lblUnit.grid(row=idx, column=3)
            idx += 1
        # Import Config
        self.lblImport.grid(row=idx, column=0, padx=10, sticky="w")
        self.cmbImport.grid(row=idx, column=1, columnspan=3, sticky="ew", padx=5)
        # Buttons
        self.btnApply.grid(row=0, column=0, sticky="ew", ipadx=5, padx=10)
        self.btnCancel.grid(row=0, column=1, sticky="ew", ipadx=5, padx=10)
        self.btnReset.grid(row=0, column=2, sticky="ew", ipadx=5, padx=10)
        

    def reset_layout(self):
        self.pack_forget()
        self.grid_forget()
        
        for panel in self.winfo_children():
            panel.pack_forget()
            panel.grid_forget()
            if type(panel) in (tk.PanedWindow,tk.Frame): 
                for widget in panel.winfo_children():
                    widget.pack_forget()
                    widget.grid_forget()

## USEFULL FUNCTIONS
def searchByName(data: dict, name: str) -> dict:
    for val in data.values():
        if val["name"] == name:
            return val


## TRASH

# It work !
def testAxisConstruct():
    root = tk.Tk()
    frame = tk.Frame(root)

    nb_axis = 2
    axis = ('X','Y','Z')
    taxis = [ AxisLabeledEntry(frame,axis[nAxis],"mm") for nAxis in range(nb_axis) ]

    frame.pack()
    root.mainloop()

# It work !
def testIconButton():
    root = tk.Tk()
    frame = tk.Frame(root)

    icon = tk.PhotoImage(file=config.path+"X_symbol.png")
    btnIcon = tk.Button(frame, image=icon, relief=tk.FLAT, bg="#afafaf", command=lambda s="pressed":print(s))
    btnIcon.pack()

    inpEntry = DoubleVar()
    inpEntry.set(45)
    entry = tk.Entry(frame, textvariable=inpEntry, bg="#ffff66", disabledbackground="#ddddaa")
    entry.config(state="disabled")
    inpEntry.set(100)
    entry.pack()

    frame.pack()
    root.mainloop()

def testAxisFrame():
    root = tk.Tk()

    frame = AxisFrame(root, ('X','Y','Z'))
    
    frame.pack()
    root.mainloop()

def testSettingsFrame():
    root = tk.Tk()

    ex_options = {
        "parameters": {
            "speed": {
                "name": "Speed",
                "unit": "mm",
                "default": 500
            },
            "stepscaleX": {
                "name": "Step Scale",
                "unit": "step/mm",
                "default": "platine2",
                "options": { # from json
                    "platine1": {
                        "name": "Platine 1",
                        "value": 100
                    },
                    "platine2": {
                        "name": "Platine 2",
                        "value": 200
                    }
                }
            },
            "stepscaleY": {
                "name": "Step Scale",
                "unit": "step/mm",
                "default": 150,
                "options": { # from json
                    "platine1": {
                        "name": "Platine 1",
                        "value": 100
                    },
                    "platine2": {
                        "name": "Platine 2",
                        "value": 200
                    }
                }
            }
        },
        "configs": {
            "config1": {
                "name": "Config 1",
                "speed": 60,
                "stepscaleX": "platine1"
            },
            "config2": {
                "name": "Config 2",
                "speed": 75,
                "stepscaleX": "platine2"
            }
        }
    }
    frame = SettingsFrame(root,options=ex_options)

    frame.pack()
    root.mainloop()

def testDict():
    dico = {
        "platine1": {
            "name": "Platine 1",
            "value": 100
        },
        "platine2": {
            "name": "Platine 2",
            "value": 200
        }
    }
    print(dico["platine1"])
    for key,val in dico.items():
        print(key,val["name"])


if __name__ == "__main__":
    print("start")

    # testIconButton()
    # testAxisFrame()
    testSettingsFrame()

    print("end")