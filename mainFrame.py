import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import mytools
import models
import communications as cmds
import config

class MainApp(tk.Tk):
    def __init__(self, axis_names, title: str ="", *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.title(title)
        self.frame = mytools.ScrollableFrame(self)
        self.frame.pack(expand=True, fill="both")
        self.frame.canvas.pack(padx=25, pady=10)

        # self.label = ttk.Label(self, text="Shrink the window to activate scrollbar")
        # self.label.pack()
        # for i in range(10):
        #     ttk.Button(self.frame.interior, text=f"Button {i}").pack(padx=10, pady=5)
        # self.frame.interior.config(style="TFrame")
        # stylesheet = ttk.Style().configure("TFrame", background="#0fff00")

        self.axis: list = axis_names

        self.mSettings = models.ModelSettings(self.axis)
        self.mSettings.loadSettings(config.path)
        self.mSettings.applySettingsFromData()
        speeds = { axis:100 for axis in self.axis }
        self.mControl = models.ModelControl(self.axis, cmds.CSeries(axis_speeds=speeds), settings=self.mSettings)

        self.btnOpenSettings = tk.Button(self.frame.interior, text="Settings", command=self.openSettings)
        self.btnOpenSettings.pack(expand=True, fill="both")
        # self.settingsFrame = mytools.SettingsFrame(self.frame.interior, self.mSettings.getSettingsDict())
        self.incrFrame = self.createIncrementalFrame(self.frame.interior)
        self.absFrame = self.createAbsoluteFrame(self.frame.interior)
        self.controlGeneralFrame = mytools.ControlGeneralFrame(self.frame.interior, self.axis)

        self.controlGeneralFrame.addCallback("stop",self.mControl.stop)
        self.controlGeneralFrame.addCallback("setzero",self.setZero)
        self.controlGeneralFrame.addCallback("gozero",self.goZero)

        self.controlFrame = mytools.ControlFrame(self.frame.interior)
        self.control_dict = {
            "incrmove": {
                "name": "Incrémental",
                "frame": self.incrFrame
            },
            "absmove": {
                "name": "Absolu",
                "frame": self.absFrame
            }
        }
        self.controlFrame.setOptions(self.control_dict)

        # Dont work well, bad placement unil first control change then its good
        # self.reset_layout()
        # self.apply_layout()

    def updateCurrentPosition(self):
        for axis,inpCurPos in self.controlGeneralFrame.inpAxisValues.items():
            inpCurPos.set(self.mControl.values[axis])

    def incrMove(self, sign: str, axis: str):
        if self.incrAxis.axis[self.axis.index(axis)].inpSpeedAxis.get() > 0 and self.incrAxis.axis[self.axis.index(axis)].inpAxis.get() != 0:
            incrMoveDict = {}
            incrSpeedDict = {}
            for oneAxis in self.axis:
                incrMoveDict.update({
                    oneAxis:0
                })
                incrSpeedDict.update({
                    oneAxis:0
                })
            incrMoveDict[axis]  = self.incrAxis.axis[self.axis.index(axis)].inpAxis.get()
            incrSpeedDict[axis] = self.incrAxis.axis[self.axis.index(axis)].inpSpeedAxis.get()
            if sign == "-":
                incrMoveDict[axis] = -incrMoveDict[axis]
            
            cmd = self.mControl.incrMove(incrMoveDict,incrSpeedDict)
            self.inpIncrCmd.set(cmd[:-2])
            self.updateCurrentPosition()

    def absMove(self):
        absMoveDict = {}
        absSpeedDict = {}
        for oneAxis in self.axis:
            absMoveDict.update({
                oneAxis: self.absAxis.axis[self.axis.index(oneAxis)].inpAxis.get()
            })
            absSpeedDict.update({
                oneAxis: self.absAxis.axis[self.axis.index(oneAxis)].inpSpeedAxis.get()
            })
        cmd = self.mControl.absMove(absMoveDict,absSpeedDict)
        self.inpAbsCmd.set(cmd[:-2])
        self.updateCurrentPosition()

    def setZero(self):
        self.mControl.setZero()
        self.updateCurrentPosition()

    def goZero(self):
        self.mControl.goZero()
        self.updateCurrentPosition()

    def openSettings(self):
        self.settingWindow = tk.Toplevel(self)
        self.settingWindow.title("Settings")

        self.mSettings.loadSettings(config.path)

        self.settingsFrame = mytools.SettingsFrame(self.settingWindow, self.mSettings.getSettingsDict())
        self.settingsFrame.pack(expand=True, fill="both")

        self.settingsFrame.btnApply.config(command=self.applySettings)
        # self.settingsFrame.addApplyCallback(
        #     lambda  port=self.settingsFrame.parameters["port"].inpValue,
        #             stepscales= stepScalesDict,
        #             baudrate=self.settingsFrame.parameters["controller"].inpValue:
        #             self.mSettings.applySettings(port,stepscales,baudrate)
        # )
        # self.settingsFrame.addApplyCallback(settingWindow.destroy)

        self.settingWindow.mainloop()

    def applySettings(self):
        
        platinesDict = {}
        for key,stepscale in self.settingsFrame.parameters.items():
            if "platine" in key:
                platinesDict.update({
                    key[len("platine"):]: stepscale.cmbSetting.get()
                })
        
        self.mSettings.saveSettings(
            config.path,
            port=self.settingsFrame.parameters["port"].cmbSetting.get(),
            platines=platinesDict,
            controller=self.settingsFrame.parameters["controller"].cmbSetting.get()
        )

        self.settingWindow.destroy()

    def createIncrementalFrame(self, master: tk.Widget) -> tk.Frame:
        axisBgColors = ["#F15A5A","#71C257","#DDC96A"]
        axisFgColors = ["#FFFFFF","#FFFFFF","#FFFFFF"]

        incrFrame = tk.Frame(master)
        axis_delta = [ f"Δ{oneAxis}" for oneAxis in self.axis ]
        self.incrAxis = mytools.AxisFrame(incrFrame, axis_delta)
        self.incrButtons = mytools.AxisButtonsFrame(incrFrame, self.axis)

        # Axis label colors
        idxAxis = 0
        for oneAxis in self.incrAxis.axis:
            oneAxis.lblAxis.config(fg=axisBgColors[idxAxis])
            idxAxis += 1

        idxAxis = 0
        for oneBtnAxis in self.incrButtons.btnAxis:
            oneBtnAxis: mytools.AxisButtons
            oneBtnAxis.btnPlus  .config(
                command=lambda sign="+", axis=self.axis[idxAxis]: self.incrMove(sign,axis), 
                bg=axisBgColors[idxAxis],
                fg=axisFgColors[idxAxis]
            )
            oneBtnAxis.btnMinus .config(
                command=lambda sign="-", axis=self.axis[idxAxis]: self.incrMove(sign,axis),
                bg=axisBgColors[idxAxis],
                fg=axisFgColors[idxAxis]
            )
            idxAxis += 1

        self.incrReverse = tk.Frame(incrFrame)
        self.incrReverse.rowconfigure((0),weight=1,uniform='a')
        self.incrReverse.columnconfigure(tuple(range(len(self.axis))), weight=1, uniform='a')
        
        self.btnIncrReverse = []
        idxAxis = 0
        for axis_name in self.axis:
            self.btnIncrReverse.append(
                tk.Button(
                    self.incrReverse, 
                    text=f"Reverse {axis_name} axis", 
                    command=lambda ax=axis_name:self.incrButtons.reverseButtons(ax),
                    bg=axisBgColors[idxAxis],
                    fg=axisFgColors[idxAxis]
                ).grid(row=0,column=idxAxis, sticky="ew", padx=5)
            )
            idxAxis += 1
        self.incrReverse.pack(expand=True,fill="both")

        self.incrDisplayCmd = tk.Frame(incrFrame)
        self.incrDisplayCmd.rowconfigure((0),weight=1,uniform='a')
        self.incrDisplayCmd.columnconfigure((0), weight=1, uniform='a')
        self.incrDisplayCmd.columnconfigure((1), weight=2, uniform='a')
        self.lblIncrCmdTitle = tk.Label(self.incrDisplayCmd, text="Command").grid(row=0,column=0,sticky="ew", pady=10)
        self.inpIncrCmd = tk.StringVar()
        self.inpIncrCmd.set("@lorem ipsum dolor sit")
        self.lblIncrCmd = tk.Label(
            self.incrDisplayCmd, 
            textvariable=self.inpIncrCmd,
            relief="solid",
            background="#dddddd",
            fg="#595959",
            borderwidth=2,
            anchor="w",
            font=Font(family="Helvetica", slant="italic", size=10)
        ).grid(row=0,column=1, sticky="ew")
        self.incrDisplayCmd.pack(expand=True, fill="both")

        return incrFrame
    
    def createAbsoluteFrame(self, master: tk.Widget) -> tk.Frame:
        absFrame = tk.Frame(master)
        self.absAxis = mytools.AxisFrame(absFrame, self.axis)

        self.absDisplayCmd = tk.Frame(absFrame)
        self.absDisplayCmd.rowconfigure((0),weight=1,uniform='a')
        self.absDisplayCmd.columnconfigure((0), weight=1, uniform='a')
        self.absDisplayCmd.columnconfigure((1), weight=2, uniform='a')
        self.lblAbsCmdTitle = tk.Label(self.absDisplayCmd, text="Command").grid(row=0,column=0,sticky="ew", pady=10)
        self.inpAbsCmd = tk.StringVar()
        self.inpAbsCmd.set("@lorem ipsum")
        self.lblAbsCmd = tk.Label(
            self.absDisplayCmd, 
            textvariable=self.inpAbsCmd,
            relief="solid",
            background="#dddddd",
            fg="#595959",
            borderwidth=2,
            anchor="w",
            font=Font(family="Helvetica", slant="italic", size=10)
        ).grid(row=0,column=1, sticky="ew")
        self.absDisplayCmd.pack(expand=True, fill="both")

        self.absBtnMove = tk.Button(
            absFrame, 
            text="Move",
            command=self.absMove, 
            bg="#6873D5", 
            fg="#FFFFFF", 
            activebackground="#4853B5",
            activeforeground="#DDDDDD",
            font=Font(family="Helvetica", size=12)
        ).pack(expand=True, fill="x")
        return absFrame

    def apply_layout(self):
        self.frame.pack(expand=True, fill="both")
        self.frame.canvas.pack(expand=True, side="left", fill="both", padx=25, pady=10)

        self.controlGeneralFrame.pack(expand=True, fill="x")
        self.controlFrame.pack(expand=True, fill="x")
        # self.controlGeneralFrame.apply_layout()
        # self.controlFrame.apply_layout()

    def reset_layout(self):
        self.frame.pack_forget()
        self.frame.canvas.pack_forget()

        # self.controlFrame.pack_forget()
        # self.controlGeneralFrame.pack_forget()
        # self.controlGeneralFrame.reset_layout()
        # self.controlFrame.reset_layout()


if __name__ == "__main__":
    print("start")

    app = MainApp(title="test main",axis_names=('X','Y','Z'))
    app.geometry("500x650")

    app.mainloop()
