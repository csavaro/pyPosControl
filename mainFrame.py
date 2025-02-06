import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import mytools
import models
import config

class MainApp(tk.Tk):
    def __init__(self, axis_names, title: str ="", *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.title = title
        self.frame = mytools.ScrollableFrame(self)
        self.frame.pack(expand=True, fill="both")
        self.frame.canvas.pack(padx=25, pady=10)

        # self.label = ttk.Label(self, text="Shrink the window to activate scrollbar")
        # self.label.pack()
        # for i in range(10):
        #     ttk.Button(self.frame.interior, text=f"Button {i}").pack(padx=10, pady=5)
        # self.frame.interior.config(style="TFrame")
        # stylesheet = ttk.Style().configure("TFrame", background="#0fff00")

        self.axis = axis_names

        self.mSettings = models.ModelSettings(self.axis)
        self.mSettings.loadSettings(config.path)

        # TO_IMPLEMENT
        self.btnOpenSettings = tk.Button(self.frame.interior, text="Settings", command=self.openSettings)
        self.btnOpenSettings.pack(expand=True, fill="both")
        # self.settingsFrame = mytools.SettingsFrame(self.frame.interior, self.mSettings.getSettingsDict())
        self.incrFrame = self.createIncrementalFrame(self.frame.interior)
        self.absFrame = self.createAbsoluteFrame(self.frame.interior)
        self.controlGeneralFrame = mytools.ControlGeneralFrame(self.frame.interior, self.axis)

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

    def openSettings(self):
        settingWindow = tk.Tk()
        settingWindow.title = "Settings"

        self.settingsFrame = mytools.SettingsFrame(settingWindow, self.mSettings.getSettingsDict())
        self.settingsFrame.pack(expand=True, fill="both")

        settingWindow.mainloop()

    def createIncrementalFrame(self, master: tk.Widget) -> tk.Frame:
        incrFrame = tk.Frame(master)
        self.incrAxis = mytools.AxisFrame(incrFrame, self.axis)
        self.incrButtons = mytools.AxisButtonsFrame(incrFrame, self.axis)

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
                    command=lambda ax=axis_name:self.incrButtons.reverseButtons(ax)
                ).grid(row=0,column=idxAxis, sticky="ew", padx=5)
            )
            idxAxis += 1
        self.incrReverse.pack(expand=True,fill="both")

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

    app.mainloop()
