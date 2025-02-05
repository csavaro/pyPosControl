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
        - name: axis name
        - lblAxis: label, title of the axis.
        - spbAxis: spinbox, input of the axis value.
        - inpAxis: doublevar, value from the input spbAxis.
        - lblUnit (optional): label, additional info like unit of the axis value.
        - spbSpeedAxis: spinbox, input of the axis speed value.
        - inpSpeedAxis: doublevar, value from the input spbSpeedAxis.
        - lblSpeedUnit (optional): label, additional info like unit of the axis speed value.
    """
    def __init__(self,master: tk.Widget,label: str,unit: str = None, speed: bool = True):
        self.name = label
        self.lblAxis = tk.Label(master, text=label)
        self.inpAxis = DoubleVar(value=0.0)
        self.spbAxis = tk.Spinbox(master, textvariable=self.inpAxis, from_=-8000000, to=8000000, width=20)
        if unit:
            self.lblUnit = tk.Label(master, text=unit)
        self.hasSpeed = speed
        if speed:
            self.inpSpeedAxis = DoubleVar(value=0.0)
            self.spbSpeedAxis = tk.Spinbox(master, textvariable=self.inpSpeedAxis, from_=0, to=8000000, width=20)
            if unit:
                self.lblSpeedUnit = tk.Label(master, text=unit+"/s")
    
        # Callbacks
        self.inpSpeedAxis.trace_add("write", lambda name,index,mode : self.checkSpeed())

    def checkAxis(self):
        pass

    def checkSpeed(self):
        inpOk = checkPosInput(self.inpSpeedAxis)
        pass

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

        self.pnlAxis = [ tk.Frame(self) for i in range(len(axis_names)) ]
        self.axis = [ AxisLabeledEntry(self.pnlAxis[axis_names.index(axis_name)],axis_name,"mm",True) for axis_name in axis_names ]

        self.apply_layout()
        
    def apply_layout(self):
        self.pack(fill="x")
        self.columnconfigure((0), weight=1, uniform='a')
        # self.rowconfigure(tuple(range(len(self.axis))), weight=1, uniform='a')
        self.rowconfigure((0,1,2), weight=1, uniform='a')

        for idxAxis in range(len(self.axis)):
            # Panels
            self.pnlAxis[idxAxis].grid(row=idxAxis, column=0, sticky="ew", pady=10, padx=10)
            self.pnlAxis[idxAxis].columnconfigure((0,2,4), weight=1, uniform='a')
            self.pnlAxis[idxAxis].columnconfigure((1,3), weight=3, uniform='a')
            self.pnlAxis[idxAxis].rowconfigure((0), weight=1, uniform='a')
            # Components
            self.axis[idxAxis].lblAxis.grid(column=0, row=idxAxis, sticky="w")
            self.axis[idxAxis].spbAxis.grid(column=1, row=idxAxis, sticky="ew")
            # self.axis[idxAxis].spbAxis.config(from_=0)
            if self.axis[idxAxis].lblUnit:
                self.axis[idxAxis].lblUnit.grid(column=2, row=idxAxis, sticky="ew")
            if self.axis[idxAxis].hasSpeed:
                self.axis[idxAxis].spbSpeedAxis.grid(column=3, row=idxAxis, sticky="ew")
                if self.axis[idxAxis].lblSpeedUnit:
                    self.axis[idxAxis].lblSpeedUnit.grid(column=4, row=idxAxis, sticky="ew")

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
        if value is None:
            self.inpValue.set('')
            self.entValue.delete(0,'end')
            if self.cmbSetting:
                self.cmbSetting.set('')
        elif self.cmbSetting:
            # Select the option if found
            if value in self.options.keys():
                self.cmbSetting.set(self.options[value]["name"])
                self.applyOption()
                return
        else:
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
                    "name": "Platine X",
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
        for key in self.options["parameters"].keys():
            val = None
            if key in self.options["configs"][target_OptionKey].keys():
                val = self.options["configs"][target_OptionKey][key]
            print(f"setting {key} as {val}")
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
        self.pnlSettings.columnconfigure((0,2,3), weight=1, uniform='a')
        self.pnlSettings.columnconfigure((1), weight=2, uniform='a')

        self.pnlButtons.grid(row=len(self.parameters)+2, column=0, sticky="ew")
        self.pnlButtons.rowconfigure((0), weight=1, uniform='a')
        self.pnlButtons.columnconfigure((0,1,2), weight=1, uniform='a')

        # Components
        # Parameters
        idx = 0
        for param in self.parameters.values():
            param.lblSetting.grid(row=idx, column=0, pady=5, padx=10, sticky="w")
            param.entValue.grid(row=idx, column=2, sticky="ew", padx=5)
            if param.cmbSetting:
                param.cmbSetting.grid(row=idx, column=1, sticky="ew", padx=5)
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

class ControlFrame(tk.Frame):
    """
    Summary:
        Frame with navbar buttons to display frames/functionalities.
        For example to swap from absolute movement to absolute movement.
    """
    def __init__(self, master: tk.Widget, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # ! TO CLEANUP !
        # Example
        # ex_options = {
        #     "control1": {
        #         "name": "Incrémental",
        #         "frame": mytools.AxisFrame(self,('X','Y','Z'))
        #     },
        #     "control2": {
        #         "name": "Absolu",
        #         "frame": mytools.AxisFrame(self,('X','Y'))
        #     },
        # }
        
        self.options = {}
        self.btnNav = {}
        self.pnlNavbar = tk.PanedWindow(self, orient=tk.HORIZONTAL, relief="solid", borderwidth=1)
        self.content = None
        self.apply_layout()

    def setOptions(self, options: dict):
        self.options = options
        self.btnNav = {}
        for key,oneOption in options.items():
            oneOption["frame"].pack_forget()
            oneOption["frame"].grid_forget()
            self.btnNav.update(
                {
                    key:
                    tk.Button(
                        self.pnlNavbar,
                        text=oneOption["name"],
                        command=lambda k=key: self.activateContent(k),
                        relief=tk.FLAT
                    )
                }
            )
        self.apply_layout()
        if len(self.btnNav) >= 1:
            self.activateContent(list(self.btnNav.keys())[0])

    def setContent(self, frame: tk.Frame, event=None):
        if self.content:
            self.content.grid_forget()
            self.content.pack_forget()
        self.content = frame
        self.apply_layout()

    def activateContent(self, button_key, event=None):
        # Mark button pressed as active
        self.btnNav[button_key].config(state="active", bg="#F8F8F8")

        # Unmark other buttons
        for key,oneBtnNav in self.btnNav.items(): 
            if key != button_key:
                oneBtnNav.config(state="normal", bg="#DDDDDD")

        # Adapt content
        self.setContent(self.options[button_key]["frame"])

    def apply_layout(self):
        self.pack(fill="x")
        
        # Panels
        self.pnlNavbar.pack(fill="x", padx=10)
        self.pnlNavbar.rowconfigure((0), weight=1, uniform='a')
        if len(self.options)>0:
            self.pnlNavbar.columnconfigure(tuple(range(len(self.options))), weight=1, uniform='a')
        else:
            self.pnlNavbar.columnconfigure((0), weight=1, uniform='a')
        if self.content:
            self.content.pack(fill="x")

        # Components
        idx = 0
        for key,oneBtnNav in self.btnNav.items():
            oneBtnNav.grid(row=0, column=idx, sticky="ew", ipady=5)
            idx += 1

    def reset_layout(self):
        print("reset layout")
        self.pack_forget()
        self.grid_forget()

        for child in self.winfo_children():
            print("resetting",child)
            child.pack_forget()
            child.grid_forget()

class AxisButtons:
    """
    Summary:
        Class containing two buttons. One with positive sign as a text, an another with minus.
    Parameters:
        - name : name of the axis those buttons should control
        - btnPlus : button for positive direction
        - btnMinus : button for negative direction
    """
    def __init__(self, master, name):
        self.name = name
        self.btnPlus = tk.Button(master, text="+")
        self.btnMinus = tk.Button(master, text="-")

    def config_both(self, *args, **kwargs):
        self.btnPlus.config(*args, **kwargs)
        self.btnMinus.config(*args, **kwargs)

class AxisButtonsFrame(tk.Frame):
    """
    Summary:
        Frame containing buttons from 1 axis up to 3. Create and position them.
    Parameters:
        - btnAxis : list, instances of AxisButton for each axis specified.
    """
    def __init__(self, master: tk.Widget, axis_names=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        if not axis_names:
            axis_names = ('X','Y','Z')

        self.btnAxis = []
        for axis_name in axis_names:
            ab = AxisButtons(self, axis_name)
            # Adjust buttons
            ab.btnPlus.config(height=1, width=2, font=("Times",30))
            ab.btnMinus.config(height=1, width=2, font=("Times",30))
            self.btnAxis.append(ab) 


        self.apply_layout()
    
    def apply_layout(self):
        self.pack(fill="x", padx=5, pady=5)
        if len(self.btnAxis) == 1:
            self.rowconfigure((0), weight=1, uniform='a')
            self.columnconfigure((0,1), weight=1, uniform='a')

            self.btnAxis[0].btnPlus .grid(row=0, column=1, sticky="ew", padx=5, pady=5)
            self.btnAxis[0].btnMinus.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        elif len(self.btnAxis) == 2:
            self.rowconfigure((0,1,2), weight=1, uniform='a')
            self.columnconfigure((0,1,2), weight=1, uniform='a')

            self.btnAxis[0].btnPlus .grid(row=1, column=2, sticky="ew", padx=5, pady=5)
            self.btnAxis[0].btnMinus.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
            self.btnAxis[1].btnPlus .grid(row=0, column=1, sticky="ew", padx=5, pady=5)
            self.btnAxis[1].btnMinus.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        elif len(self.btnAxis) == 3:
            self.rowconfigure((0,1,2), weight=1, uniform='a')
            self.columnconfigure((0,1,2,3,4,5), weight=1, uniform='a')

            self.btnAxis[0].btnPlus .grid(row=1, column=4, columnspan=2, sticky="ew", padx=5, pady=5)
            self.btnAxis[0].btnMinus.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            self.btnAxis[1].btnPlus .grid(row=0, column=2, columnspan=2, sticky="ew", padx=5, pady=5)
            self.btnAxis[1].btnMinus.grid(row=2, column=2, columnspan=2, sticky="ew", padx=5, pady=5)
            self.btnAxis[2].btnPlus .grid(row=1, column=3, sticky="ew", padx=5, pady=5)
            self.btnAxis[2].btnMinus.grid(row=1, column=2, sticky="ew", padx=5, pady=5)

    def reset_layout(self):
        self.pack_forget()
        self.grid_forget()

        for child in self.winfo_children():
            child.pack_forget()
            child.grid_forget()

    def reverseButtons(self, axis):
        target_btn: AxisButtons = None
        for btn in self.btnAxis:
            if btn.name == axis: 
                target_btn = btn
                break
        if target_btn:
            trow = target_btn.btnPlus.grid_info()["row"]
            tcol = target_btn.btnPlus.grid_info()["column"]
            target_btn.btnPlus.grid(row=target_btn.btnMinus.grid_info()["row"],column=target_btn.btnMinus.grid_info()["column"])
            target_btn.btnMinus.grid(row=trow, column=tcol)
            

class ControlGeneralFrame(tk.Frame):
    """
    Summary:
        Frame that display axis values, with 3 buttons to do main actions quickly.
        Contain a button Stop, Set to zero and Go to zero plus labels for axis current values.
    Parameters:
        - btnStop : button, labeled "Stop movements", meant to send a stop signal.
        - btnSetZero : button, labeled "Set as zero", meant to set current axis values to zero.
        - btnGoZero : button, labeled "Go to zero", meant send signals to get the current axis values to zero.
        - lblNames : list of Label, axis names in front of their current values.
        - inpAxisValues : dict of axis_names:DoubleVar, inputs containing current axis values.
        - lblAxisValues : list of Label, labels displaying inpAxisValues values.
        - callbacks : dict of btnName:list of functions, attribute callbacks to buttons of the frame.
    """
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
        # call callbacks
        for cb in self.callbacks[self.STOP]: cb()
    
    def setZero(self):
        # call callbacks
        for cb in self.callbacks[self.SETZERO]: cb()

    def goZero(self):
        # call callbacks
        for cb in self.callbacks[self.GOZERO]: cb()

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

class ScrollableFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Create scrollable shit
        self.sclBar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.sclBar.pack(fill=tk.Y, side=tk.RIGHT, expand=False)

        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, width=200, height=300, yscrollcommand=self.sclBar.set)
        self.canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        
        self.sclBar.config(command=self.canvas.yview)

        # Create scrollable frame
        self.interior = ttk.Frame(self.canvas)
        self.interior.bind("<Configure>", self._configure_interior)
        self.canvas.bind("<Configure>", self._configure_canvas)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=tk.NW)

    def _configure_interior(self, event):
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion=(0, 0, size[0], size[1]))
        if self.interior.winfo_reqwidth() != self.canvas.winfo_reqwidth():
            self.canvas.config(width=self.interior.winfo_reqwidth())
        
    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
## --------------------------------------
## USEFULL FUNCTIONS

def searchByName(data: dict, name: str) -> dict:
    for val in data.values():
        if val["name"] == name:
            return val

def checkPosInput(input: DoubleVar):
    """
    Check if an input number like DoubleVar is negative, and remove it's sign if so.
    Also return -1 if the input value is a wrong type.
    """
    try:
        if input.get() < 0:
            input.set(-input.get())
        return 0
    except tk.TclError as e:
        print("wrong value type.")
        print(e)
        return -1


## --------------------------------------
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
                "name": "Platine X",
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
                "name": "Platine Y",
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

def testControlFrame():
    print("stat testControlFrame")
    root = tk.Tk()

    cf = ControlFrame(root)

    ex_options = {
            "control1": {
                "name": "Incrémental",
                "frame": AxisFrame(cf,('X','Y','Z'))
            },
            "control2": {
                "name": "Absolu",
                "frame": AxisFrame(cf,('X','Y'))
            },
        }
    
    ex_options["control2"]["frame"].config(bg="#ff00ff", borderwidth=2, relief="groove")

    cf.setOptions(ex_options)
    # cf.reset_layout()

    cf.pack()
    tk.mainloop()

def testAxisButtonsFrame():
    root = tk.Tk()

    axis = ('X','Y','Z')

    abf = AxisButtonsFrame(root, axis)

    root.mainloop()

def testControlGeneralFrame():
    print("start testControlGeneralFrame")
    root = tk.Tk()

    cgf = ControlGeneralFrame(root, ('X','Y','Z'))

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
    # testSettingsFrame()
    # testControlFrame()
    # testAxisButtonsFrame()
    testControlGeneralFrame()

    print("end")