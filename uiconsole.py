import models
from pathlib import Path
from connection import MissingValue
import communications as cmds

# Current path
path = str(Path(__file__).parent.absolute())+"\\"

class UiConsole:
    def __init__(self, axis_names):
        self.axis = axis_names

        self.mSettings = models.ModelSettings(self.axis)
        self.mSettings.loadSettings(path)
        self.mSettings.applySettingsFromData()
        self.mSettings.applyDefault()
        self.mControl = models.ModelControl(self.axis, cmds.CSeries(axis_speeds=self.mSettings.default_speeds), settings=self.mSettings)

        self.actionDict = {
            "0": {
                "label": "Quit",
                "action": self.quit
            },
            "1": {
                "label": "Display current position",
                "action": self.printCurrentPosition
            },
            "2": {
                "label": "Go to settings",
                "action": self.settingsMenu
            },
            "3": {
                "label": "Incremental move",
                "action": self.incrMove
            },
            "4": {
                "label": "Absolute move",
                "action": self.absMove
            },
            "5": {
                "label": "Go to zero",
                "action": self.goZero
            },
            "6": {
                "label": "Set as zero",
                "action": self.setZero
            },
            "s": {
                "label": "Stop signal",
                "action": self.stop
            }
        }

        self.settingsDict = {
            "0": {
                "label": "Go back to menu",
                "action": lambda s="> going back to menu": print(s)
            },
            "1": {
                "label": "Display current settings",
                "action": self.printCurrentSettings
            },
            "c": {
                "label" : "Change controller",
                "action": self.controllerMenu
            },
            "p": {
                "label": "Change port",
                "action": self.portMenu
            }
        }
        for oneAxis in self.axis:
            self.settingsDict.update({
                f"s{oneAxis}": {
                    "label": f"Change platine {oneAxis}",
                    "action": lambda a=oneAxis: self.platinesMenu(a)
                }
            })

    def mainMenu(self):
        self.menu(self.actionDict, "0", "Main menu")

    def settingsMenu(self):
        self.settingsData = self.mSettings.getSettingsDict()
        self.menu(self.settingsDict, "0", "Settings")

    def platinesMenu(self, axis: str):
        platinesDict = {
            "0": {
                "label": "Go back to settings",
                "action": lambda s="> going back to settings": print(s)
            },
            "e": {
                "label": "Empty",
                "action": lambda pd={ axis: "" }: self.saveSettings(platines=pd)
            }
        }
        idx = 1
        for onePlatine in self.mSettings.platinesData.values():
            print("CREATING",onePlatine)
            # add decoration to display on the current platine
            prefix = ""
            if onePlatine["name"] == self.settingsData['parameters'][f'platine{axis}']['default']:
                prefix = "* "
            # create option
            platinesDict.update({
                str(idx): {
                    "label": prefix+onePlatine["name"],
                    "action": lambda pd={ axis: onePlatine["name"] }: self.saveSettings(platines=pd)
                }
            })
            idx += 1

        self.menu(platinesDict, "0", "Choosing platine")

    def controllerMenu(self):
        controllersDict = {
            "0": {
                "label": "Go back to settings",
                "action": lambda s="> going back to settings": print(s)
            },
            "e": {
                "label": "Empty",
                "action": lambda cd="": self.saveSettings(controller=cd)
            }
        }

        idx = 1
        for oneController in self.mSettings.controllersData.values():
            print("CREATING",oneController)
            # add decoration to display on the current platine
            prefix = ""
            if oneController["name"] == self.settingsData['parameters']['controller']['default']:
                prefix = "* "
            # create option
            controllersDict.update({
                str(idx): {
                    "label": prefix+oneController["name"],
                    "action": lambda cd=oneController["name"]: self.saveSettings(controller=cd)
                }
            })
            idx += 1
        
        self.menu(controllersDict, "0", "Choosing controller")

    def portMenu(self):
        print("not implemented yet")

        portsDict = {
            "0": {
                "label": "Go back to settings",
                "action": lambda s="> going back to settings": print(s)
            },
            "e": {
                "label": "Empty",
                "action": lambda p="": self.saveSettings(port=p)
            }
        }

        idx = 1
        for onePort in self.mSettings.portsData.values():
            print("CREATING",onePort)
            # add decoration to display on the current platine
            prefix = ""
            if onePort["name"] == self.settingsData['parameters']['port']['default']:
                prefix = "* "
            # create option
            portsDict.update({
                str(idx): {
                    "label": prefix+onePort["name"],
                    "action": lambda p=onePort["name"]: self.saveSettings(port=p)
                }
            })
            idx += 1
        
        self.menu(portsDict, "0", "Choosing port")

    def incrMove(self):
        aVals,aSpeeds = self.inputCmd()
        try:
            if aVals and aSpeeds:
                cmd = self.mControl.incrMove(aVals,aSpeeds)
        except MissingValue as e:
            print("ERROR: MissingValue",e)

    def absMove(self):
        aVals,aSpeeds = self.inputCmd()
        try:
            if aVals and aSpeeds:
                cmd = self.mControl.absMove(aVals,aSpeeds)
        except MissingValue as e:
            print("ERROR: MissingValue",e)

    def goZero(self):
        try:
            self.mControl.goZero()
        except MissingValue as e:
            print("ERROR: MissingValue",e)

    def setZero(self):
        try:
            self.mControl.setZero()
        except MissingValue as e:
            print("ERROR: MissingValue",e)

    def stop(self):
        try:
            self.mControl.stop()
        except MissingValue as e:
            print("ERROR: MissingValue",e)

    def inputCmd(self):
        axis_vals = { oneAxis:0 for oneAxis in self.axis }
        axis_speeds = { oneAxis:0 for oneAxis in self.axis }

        incorrectFormat = True
        while incorrectFormat:
            print("Enter the movement. Axis order is "+str(self.axis)+". Format is {x_val,x_speed,y_val,y_speed} etc. 0 to quit")
            uCmd = input()
            if uCmd == "0":
                return 0,0
            try:
                spCmd = uCmd.split(",")
                if len(spCmd) != len(self.axis)*2:
                    print(f"Wrong! should've been {len(self.axis)*2}, not {len(spCmd)}. Use , to separate values.")
                else:
                    for i in range(0,len(spCmd),2):
                        axis_vals[self.axis[int(i/2)]] = float(spCmd[i])
                        axis_speeds[self.axis[int(i/2)]] = float(spCmd[i+1])

                    incorrectFormat = False

            except ValueError:
                exCmd = ",".join([ "45,10" for i in range(len(self.axis))])
                print(f"Wrong format! ex: {exCmd}")

        return axis_vals,axis_speeds

    def saveSettings(self, platines: dict = None, controller: str = None, port: str = None):
        if platines != None:
            plChoosed = {}
            for oneAxis in self.axis:
                # Platines to change
                if oneAxis in platines.keys():
                    plChoosed.update({
                        oneAxis: 
                        platines[oneAxis]
                    })
                # Platines to not touch
                else:
                    plChoosed.update({
                        oneAxis: 
                        self.settingsData['parameters'][f'platine{oneAxis}']['default']
                    })
            platines = plChoosed
        
        self.mSettings.saveSettings(path, port=port, platines=platines, controller=controller)
        self.mSettings.loadSettings(path)
        self.settingsData = self.mSettings.getSettingsDict()

        return "0"

    def menu(self, menuDict: dict, stop_inp: str, title: str = ""):
        choice = -1

        while choice != stop_inp:
            print(title+" : Choose an option")
            for key,content in menuDict.items():
                print(f"{key} - {content['label']}")
            
            choice = input()

            if choice in menuDict.keys():
                ret = menuDict[choice]["action"]()
                if ret != None:
                    choice = ret
            else:
                print("wrong option choosed")

    def printCurrentPosition(self):
        print("Current position :")
        print(" - ".join([ f"{axis}: {pos}" for axis,pos in self.mControl.values.items() ]))

    def printCurrentSettings(self):
        print("Current settings :")
        # Platines
        for oneAxis in self.axis:
            print(f"- Platine {oneAxis} : {self.settingsData['parameters'][f'platine{oneAxis}']['default']}")
        # Controller
        print(f"- Controller : {self.settingsData['parameters']['controller']['default']}")
        # Port
        print(f"- Port : {self.settingsData['parameters']['port']['default']}")

    def quit(self):
        self.mControl.quit()

if __name__ == "__main__":
    print("starting")

    try:
        uic = UiConsole(('X','Y'))

        uic.printCurrentPosition()

        uic.mainMenu()

    finally:
        uic.mControl.quit()

    print("ended")