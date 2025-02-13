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
        print("not implemented yet")

        platinesDict = {
            "0": {
                "label": "Go back to settings",
                "action": lambda s="> going back to settings": print(s)
            }
        }
        idx = 1
        for onePlatine in self.mSettings.platinesData.values():
            print("CREATING",onePlatine)
            # scenario this platine is choosed
            plChoosed = {}
            for oneAxis in self.axis:
                if oneAxis == axis:
                    plChoosed.update({
                        oneAxis:
                        onePlatine["name"]
                    })
                else:
                    print("MAAAAAAAAAAAIS")
                    plChoosed.update({
                        oneAxis:
                        self.settingsData['parameters'][f'platine{axis}']['default']
                    })
            # create option
            platinesDict.update({
                str(idx): {
                    "label": onePlatine["name"],
                    "action": lambda pd=plChoosed: self.mSettings.saveSettings(path,platines=pd)
                }
            })
            idx += 1

        self.menu(platinesDict, "0", "Choosing platine")

    def controllerMenu(self):
        print("not implemented yet")
        pass

    def portMenu(self):
        print("not implemented yet")
        pass

    def menu(self, menuDict: dict, stop_inp: str, title: str = ""):
        choice = -1

        while choice != stop_inp:
            print(title+" : Choose an option")
            for key,content in menuDict.items():
                print(f"{key} - {content['label']}")
            
            choice = input()

            if choice in menuDict.keys():
                menuDict[choice]["action"]()
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
        uic = UiConsole(('X','Y','Z'))

        uic.printCurrentPosition()

        uic.mainMenu()

    finally:
        uic.mControl.quit()

    print("ended")