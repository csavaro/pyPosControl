import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from tkinter.messagebox import *
# import python_files.guielements as guielements
from .guielements import ScrollableFrame,ControlGeneralFrame,ControlFrame,SettingsFrame,AxisFrame,AxisButtonsFrame,AxisLabeledEntry,AxisButtons
# import python_files.models as models
from python_files.models import ModelControl, ModelSettings
# import python_files.communications as cmds
from python_files.communications import CSeries
from python_files.connection import MissingValue
from pathlib import Path

# Current path
# path = str(Path(__file__).parent.absolute())+"\\"
path = ""

class MainApp(tk.Tk):
    def __init__(self, axis_names, title: str ="", wait_ack = True, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.title(title)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.frame = ScrollableFrame(self)
        self.frame.pack(expand=True, fill="both")
        self.frame.canvas.pack(padx=25, pady=10)

        self.axis: list = axis_names

        # self.EventMoveFinished = tk.BooleanVar()
        # self.EventMoveFinished.trace_add("write",self.afterMove)

        # self.mSettings = models.ModelSettings(self.axis)
        self.mSettings = ModelSettings(self.axis, wait_ack=wait_ack)
        self.mSettings.loadSettings(path)
        self.mSettings.applySettingsFromData()
        self.mSettings.applyDefault()
        # self.mControl = models.ModelControl(self.axis, cmds.CSeries(axis_speeds=self.mSettings.default_speeds), settings=self.mSettings)
        self.mControl = ModelControl(self.axis, CSeries(axis_speeds=self.mSettings.default_speeds), settings=self.mSettings)

        self.btnOpenSettings = tk.Button(self.frame.interior, text="Settings", command=self.openSettings, font=Font(family="Helvetica",size=12))
        self.btnOpenSettings.pack(expand=True, fill="both")
        # self.settingsFrame = mytools.SettingsFrame(self.frame.interior, self.mSettings.getSettingsDict())

        self.incrFrame = self.createIncrementalFrame(self.frame.interior)
        self.absFrame = self.createAbsoluteFrame(self.frame.interior)
        self.controlGeneralFrame = ControlGeneralFrame(self.frame.interior, self.axis)

        self.controlGeneralFrame.addCallback("stop",self.stopAction)
        self.controlGeneralFrame.addCallback("setzero",self.setZeroAction)
        self.controlGeneralFrame.addCallback("gozero",self.goZeroAction)

        self.controlFrame = ControlFrame(self.frame.interior)
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

    def afterMove(self,var=None,index=None,mode=None):
        """
        Enable movement buttons and update current position labels.
        """
        # Not used
        self.changeStateMovementsButtons("normal")
        self.updateCurrentPosition()

    def updateCurrentPosition(self):
        """
        Update current position labels from model control data.
        """
        for axis,inpCurPos in self.controlGeneralFrame.inpAxisValues.items():
            inpCurPos.set(self.mControl.values[axis])

    def changeStateMovementsButtons(self, state: str):
        """
        Change the state of movement buttons, state can be set as "normal", "disabled" or "active".
        """
        # print("start ",state)
        self.controlGeneralFrame.btnGoZero.config(state=state)
        self.controlGeneralFrame.btnSetZero.config(state=state)

        if self.incrButtons:
            for incrBtn in self.incrButtons.btnAxis:
                incrBtn.btnPlus.config(state=state)
                incrBtn.btnMinus.config(state=state)
        if self.absBtnMove:
            self.absBtnMove.config(state=state)
        # print("end ",state)

    def incrMove(self, sign: str, axis: str):
        """
        Disable movement buttons, then execute the incremental movement on model control for a single axis.
        Add callbacks to enable back and update position after the move, and show error window if MissingValue is raised. 
        Parameters:
        - sign : "+" or "-", direction of the movement,
        - axis : axis on which the move need to be done.
        """
        if self.incrAxis.axis[self.axis.index(axis)].inpSpeedAxis.get() > 0 and self.incrAxis.axis[self.axis.index(axis)].inpAxis.get() != 0:

            self.changeStateMovementsButtons(tk.DISABLED)

            incrMoveDict = {}
            incrSpeedDict = {}
            for oneAxis in self.axis:
                incrMoveDict.update({
                    oneAxis:0
                })
                incrSpeedDict.update({
                    oneAxis:self.incrAxis.axis[self.axis.index(oneAxis)].inpSpeedAxis.get()
                })
            incrMoveDict[axis]  = self.incrAxis.axis[self.axis.index(axis)].inpAxis.get()
            # incrSpeedDict[axis] = self.incrAxis.axis[self.axis.index(axis)].inpSpeedAxis.get()
            if sign == "-":
                incrMoveDict[axis] = -incrMoveDict[axis]

            try:
                updateList = [self.updateCurrentPosition]
                # updateList.append(self.updateCurrentPosition)
                fail_cbs = [lambda msg="Settings are not all set", tl="Missing value": showerror(title=tl,message=msg)]
                # fail_cbs.append(lambda tl="Missing value", msg="Settings are not all set": showerror(title=tl,message=msg))
                final_cbs = [lambda s="normal": self.changeStateMovementsButtons(s)]
                # final_cbs = [lambda s=True: self.EventMoveFinished.set(s)]
                # final_cbs.append(lambda s="normal": self.changeStateMovementsButtons(s))

                cmd = self.mControl.incrMove(incrMoveDict,incrSpeedDict,callbacks=updateList,miss_val_cbs=fail_cbs,finally_cbs=final_cbs)
                # self.changeStateMovementsButtons("normal")
                self.inpIncrCmd.set(cmd)
                self.updateCurrentPosition()
            except MissingValue as e:
                print("ERROR: MissingValue",e)
                showerror(title="Missing value",message=e)

            # self.changeStateMovementsButtons("normal")

    def absMove(self):
        """
        Disable movement buttons, then execute the absolute movement on model control for all axis.
        Add callbacks to enable back and update position after the move, and show error window if MissingValue is raised. 
        """
        self.changeStateMovementsButtons("disabled")

        # # FOR DEBUG
        # p = input("enter anything to continue")

        absMoveDict = {}
        absSpeedDict = {}
        for oneAxis in self.axis:
            absMoveDict.update({
                oneAxis: self.absAxis.axis[self.axis.index(oneAxis)].inpAxis.get()
            })
            absSpeedDict.update({
                oneAxis: self.absAxis.axis[self.axis.index(oneAxis)].inpSpeedAxis.get()
            })
        try:
            # cmd = self.mControl.absMove(absMoveDict,absSpeedDict)
            updateList = [self.updateCurrentPosition]
            # updateList.append(self.updateCurrentPosition)
            fail_cbs = [lambda msg="Settings are not all set", tl="Missing value": showerror(title=tl,message=msg)]
            # fail_cbs.append(lambda tl="Missing value", msg="Settings are not all set": showerror(title=tl,message=msg))
            final_cbs = [lambda s="normal": self.changeStateMovementsButtons(s)]
            # final_cbs.append(lambda s="normal": self.changeStateMovementsButtons(s))

            cmd = self.mControl.absMove(absMoveDict,absSpeedDict,callbacks=updateList,miss_val_cbs=fail_cbs,finally_cbs=final_cbs)

            self.inpAbsCmd.set(cmd)
            self.updateCurrentPosition()
        except MissingValue as e:
            print("ERROR: MissingValue",e)
            showerror(title="Missing value",message=e)

        # self.changeStateMovementsButtons("normal")

    def stopAction(self):
        """
        Execute stop from model control. Show an error window if MissingValue is raised.
        """
        try:
            self.mControl.stop()
        except MissingValue as e:
            print("ERROR: MissingValue",e)
            showerror(title="Missing value",message=e)

    def setZeroAction(self):
        """
        Set current position as zero in model control data and update current position.
        """
        try:
            self.mControl.setZero()
            self.updateCurrentPosition()
        except MissingValue as e:
            print("ERROR: MissingValue",e)
            showerror(title="Missing value",message=e)

    def goZeroAction(self):
        """
        Disable movement buttons, then execute the go to zero movement on model control for all axis.
        Add callbacks to enable back and update position after the move, and show error window if MissingValue is raised. 
        """
        self.changeStateMovementsButtons("disabled")
        
        # # FOR DEBUG
        # p = input("enter anything to continue")

        try:
            updateList = [self.updateCurrentPosition]
            # updateList.append(self.updateCurrentPosition)
            fail_cbs = [lambda msg="Settings are not all set", tl="Missing value": showerror(title=tl,message=msg)]
            # fail_cbs.append(lambda tl="Missing value", msg="Settings are not all set": showerror(title=tl,message=msg))
            final_cbs = [lambda s="normal": self.changeStateMovementsButtons(s)]
            # final_cbs.append(lambda s="normal": self.changeStateMovementsButtons(s))

            self.mControl.goZero(callbacks=updateList, miss_val_cbs=fail_cbs, finally_cbs=final_cbs)
            self.updateCurrentPosition()
        except MissingValue as e:
            print("ERROR: MissingValue",e)
            showerror(title="Missing value",message=e)

        # self.changeStateMovementsButtons("normal")

    def closeSettings(self):
        """
        Close setting window and enable back to button to open it again.
        """
        self.settingWindow.destroy()
        self.btnOpenSettings.config(state="normal")

    def openSettings(self):
        """
        Create a setting window with the initial data from model setting.
        """
        self.btnOpenSettings.config(state="disabled")

        self.settingWindow = tk.Toplevel(self)
        self.settingWindow.protocol("WM_DELETE_WINDOW",self.closeSettings)
        self.settingWindow.title("Settings")

        self.mSettings.loadSettings(path)

        # print("\n".join([ f"{key}:: {val}" for key,val in self.mSettings.getSettingsDict().items() ]))

        self.settingsFrame = SettingsFrame(self.settingWindow, self.mSettings.getSettingsDict())
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
        """
        Save and apply current settings selected in setting window to the model setting.
        """
        platinesDict = {}
        for key,stepscale in self.settingsFrame.parameters.items():
            if "platine" in key:
                platinesDict.update({
                    key[len("platine"):]: stepscale.cmbSetting.get()
                })

        self.mSettings.saveSettings(
            path,
            port=self.settingsFrame.parameters["port"].cmbSetting.get(),
            platines=platinesDict,
            controller=self.settingsFrame.parameters["controller"].cmbSetting.get()
        )

        self.closeSettings()

    def createIncrementalFrame(self, master: tk.Widget) -> tk.Frame:
        """
        Create the incremental control frame with axis position and speed values inputs and the buttons frame to execute the movements.
        """
        # Colors
        axisBgColors = ["#F15A5A","#71C257","#DDC96A"]
        axisFgColors = ["#FFFFFF","#FFFFFF","#FFFFFF"]
        axisActBgColors = ["#B55959","#5A9746","#BCAA53"]
        axisActFgColors = ["#DEDEDE","#DEDEDE","#DEDEDE"]
        if len(self.axis) > len(axisBgColors) or len(self.axis) > len(axisFgColors):
            for i in range(len(self.axis)-len(axisBgColors)) : axisBgColors.append("#3D3D3D")
            for i in range(len(self.axis)-len(axisFgColors)) : axisFgColors.append("#FFFFFF")

        # Creating main components
        incrFrame = tk.Frame(master)
        axis_delta = [ f"Δ{oneAxis}" for oneAxis in self.axis ]
        self.incrAxis = AxisFrame(incrFrame, axis_delta)
        self.incrButtons = AxisButtonsFrame(incrFrame, self.axis)

        # Apply default values
        for axsLabEnt in self.incrAxis.axis:
            axsLabEnt: AxisLabeledEntry
            axsLabEnt.inpSpeedAxis.set(self.mSettings.default_speeds[axsLabEnt.lblAxis.cget("text")[1:]])

        # Apply axis label colors
        idxAxis = 0
        for oneAxis in self.incrAxis.axis:
            oneAxis.lblAxis.config(fg=axisBgColors[idxAxis])
            idxAxis += 1
        # Set commands on buttons
        idxAxis = 0
        for oneBtnAxis in self.incrButtons.btnAxis:
            oneBtnAxis: AxisButtons
            oneBtnAxis.btnPlus  .config(
                command=lambda sign="+", axis=self.axis[idxAxis]: self.incrMove(sign,axis), 
                bg=axisBgColors[idxAxis],
                fg=axisFgColors[idxAxis],
                activebackground=axisActBgColors[idxAxis],
                activeforeground=axisActFgColors[idxAxis]
            )
            oneBtnAxis.btnMinus .config(
                command=lambda sign="-", axis=self.axis[idxAxis]: self.incrMove(sign,axis),
                bg=axisBgColors[idxAxis],
                fg=axisFgColors[idxAxis],
                activebackground=axisActBgColors[idxAxis],
                activeforeground=axisActFgColors[idxAxis]
            )
            idxAxis += 1

        # Creating options components
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
                    fg=axisFgColors[idxAxis],
                    activebackground=axisActBgColors[idxAxis],
                    activeforeground=axisActFgColors[idxAxis]
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
        """
        Create the absolute control frame with axis position and speed values inputs and the button to execute the movement.
        """
        absFrame = tk.Frame(master)
        self.absAxis = AxisFrame(absFrame, self.axis)

        # Apply default values
        for axsLabEnt in self.absAxis.axis:
            axsLabEnt: AxisLabeledEntry
            axsLabEnt.inpSpeedAxis.set(self.mSettings.default_speeds[axsLabEnt.lblAxis.cget("text")])

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
        )
        self.lblAbsCmd.grid(row=0,column=1, sticky="ew")
        self.absDisplayCmd.pack(expand=True, fill="both")

        self.absBtnMove = tk.Button(
            absFrame, 
            text="Move",
            command=self.absMove, 
            bg="#6873D5", 
            fg="#FFFFFF", 
            activebackground="#4853B5",
            activeforeground="#DDDDDD",
            font=Font(family="Helvetica", size=15)
        )
        self.absBtnMove.pack(expand=True, fill="x")
        return absFrame

    def apply_layout(self):
        # Not used
        self.frame.pack(expand=True, fill="both")
        self.frame.canvas.pack(expand=True, side="left", fill="both", padx=25, pady=10)

        self.controlGeneralFrame.pack(expand=True, fill="x")
        self.controlFrame.pack(expand=True, fill="x")
        # self.controlGeneralFrame.apply_layout()
        # self.controlFrame.apply_layout()

    def reset_layout(self):
        # Not used / dont work
        self.frame.pack_forget()
        self.frame.canvas.pack_forget()

        # self.controlFrame.pack_forget()
        # self.controlGeneralFrame.pack_forget()
        # self.controlGeneralFrame.reset_layout()
        # self.controlFrame.reset_layout()
    
    def _close(self):
        """
        Make sure to end components well, quitting the potential threads running from model control for example.
        """
        # kill threads
        self.mControl.quit()
        # kill GUI
        self.quit()
        self.destroy()


if __name__ == "__main__":
    print("start")

    app = MainApp(title="test main",axis_names=('X','Y'))
    app.geometry("%dx%d" % (600,app.winfo_screenheight()))

    app.mainloop()