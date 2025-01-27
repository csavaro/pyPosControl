import tkinter as tk
from tkinter import ttk
import config
from mvpSettings import ModelSettings, PresenterSettings
from mvpControl import ModelControl, PresenterControl
import serial

class Control2Axis(tk.Tk):
    def __init__(self, title="", filepath=None):
        super().__init__()
        self.title(title)
        self.geometry("500x600")
        self.mainFrame = ttk.Frame(self)
        self.mainFrame.pack(expand=True, fill="both")

        # Models
        self.mSettings  = ModelSettings(filepath=config.path+"settings.json")
        self.mControl   = ModelControl(x_speed=50, y_speed=50, steprate=self.mSettings.steprate)

        # Presenters
        self.pSettings  = PresenterSettings(self.mainFrame, self.mSettings)
        self.pControl   = PresenterControl(self.mainFrame, self.mSettings, self.mControl)

        # Other components
        self.altframe = tk.Frame(self.mainFrame)  
        self.inpCommand = tk.StringVar()
        self.entCommand = tk.Entry(self.altframe, textvariable=self.inpCommand)
        
        self.btnApplyCmd = tk.Button(self.altframe, text="Apply Command", command=self.applyCmd, width=10, bg="#ffaaaa")
        self.btnExecute = tk.Button(self.altframe, text="Execute", command=self.executeCmd, width=10, bg="#6873D5", fg="#ffffff")

        # Interface
        self.small_layout()
        self.refreshCmd()

    def onFrameConfigure(self,event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def small_layout(self):
        print("small layout")
        self.reset_layout()
        self.mainFrame.columnconfigure((0), weight=5, uniform='a')
        self.mainFrame.rowconfigure((0),  weight=2, uniform='a')
        self.mainFrame.rowconfigure((1),  weight=4, uniform='a')
        self.mainFrame.rowconfigure((2),weight=1, uniform='a')
        self.mainFrame.pack(expand=True, fill="both")

        self.altframe.columnconfigure((0),  weight=1, uniform='a')
        self.altframe.rowconfigure((0,1,2), weight=1, uniform='a')

        # self.mainFrame  .pack(expand=True, fill="both")
        # self.pSettings  .pack(expand=True, fill="both")
        # self.pControl   .pack(expand=True, fill="both")
        # self.entCommand .pack(expand=True, fill="both")
        # self.btnExecute .pack(expand=True, fill="both")
        # self.altframe   .pack(expand=True, fill="both")
        
        self.pSettings  .grid(row=0, column=0, sticky="nsew")
        self.pControl   .grid(row=1, column=0, sticky="nsew")
        self.altframe   .grid(row=2, column=0, sticky="nsew")
        self.entCommand .grid(row=0, column=0, sticky="nsew")
        self.btnExecute .grid(row=1, column=0, sticky="nsew")
        self.btnApplyCmd.grid(row=2, column=0, sticky="nsew")

    def reset_layout(self):
        self.mainFrame.pack_forget()
        self.mainFrame.grid_forget()

        self.pSettings  .pack_forget()
        self.pControl   .pack_forget()
        self.altframe   .pack_forget()

        self.pSettings  .grid_forget()
        self.pControl   .grid_forget()
        self.altframe   .grid_forget()

    def executeCmd(self):
        if type(self.command) == str:
            self.command = bytes(self.command,"ascii")
        # with serial.Serial() as ser:
        #     ser.baudrate = self.mSettings.baudrate
        #     ser.port = self.mSettings.port
        #     ser.open()
        #     ser.write(self.command)
        #     ser.close()
        print(f"Execute: {self.command.decode('utf-8')}")
    
    def applyCmd(self):
        self.refreshCmd()

    def refreshCmd(self):
        self.command = self.mControl.getCommand()
        self.inpCommand.set(self.command.decode('utf-8'))
    
if __name__ == "__main__":
    print("start")

    app = Control2Axis("test charly2axes", filepath=config.path+"settings.json")
    app.mainloop()

    print("ended")