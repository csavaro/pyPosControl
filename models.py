import config
import json

class ModelSettings:
    axisParameters = ["stepscale"]
    
    def __init__(self, axis_names):
        self.axis = axis_names
        # link to controller class for port list
        self.port = None # from available ports
        self.stepscales = { axis_name:None for axis_name in axis_names } # platines
        self.baudrate = None # controller

    def getSettingsDict(self):
        settingDico = {
            "parameters": {},
            "configs": {}
        }
        # Parameters
        self.settingsData: dict
        for keySett,valSett in self.settingsData.items():
            isAxisRel,paramName = self.isAxisRelated(keySett)
            if inWithStartKeys(keySett, self.axisParameters) and isAxisRel:
                print("AXIS REL",keySett)
                if paramName == "stepscale":
                    print("SHOULD'VE UPDATED",keySett)
                    settingDico["parameters"].update({
                        keySett: {
                            "name": "Platine "+keySett[len(paramName):],
                            "unit": "step/mm",
                            "default": valSett,
                            "options": self.platinesData
                        }
                    })
            else:
                if keySett == "port":
                    # settingDico["parameters"].update({
                    #     keySett: {
                    #         "name": "Port",
                    #         "default": valSett,
                    #         "options": self.portsData
                    #     }
                    # })
                    pass
                elif keySett == "baudrate":
                    settingDico["parameters"].update({
                        keySett: {
                            "name": "Controller",
                            "unit": "baud/s",
                            "default": valSett,
                            "options": self.controllersData
                        }
                    })

        # Configurations
        self.configsData: dict
        for keyConf,valConf in self.configsData.items():
            valConf: dict
            confDict = { keyConf: {} }
            for keySett,valSett in valConf.items():
                if keySett in settingDico["parameters"].keys() or keySett == "name":
                    confDict[keyConf].update({
                        keySett: valSett
                    })
            settingDico["configs"].update(confDict)
        
        return settingDico

    def isAxisRelated(self, data: str):
        """
        First return: true if end of string data is in self.axis.
        Second return: if found, return data without axis string, else return empty string.
        """
        for oneAxis in self.axis:
            if oneAxis == data[-len(oneAxis):]:
                return True,data[:-len(oneAxis)]
        return False,""

    def loadSettings(self, path):
        with open(path+"settings_files\\save.json","r") as saveFile:
            saveData = json.load(saveFile)
            filesData = saveData["files"]
            self.settingsData = saveData["settings"]
            self.defaultData = saveData["default"]

        with open(filesData["path"]+filesData["platine"],"r") as platinesFile:
            platinesRawData: dict = json.load(platinesFile)
            self.platinesData = {}
            for key,values in platinesRawData.items():
                self.platinesData.update({
                    key: {
                        "name": values["name"],
                        "value": values["stepscale"]
                    }
                })

        with open(filesData["path"]+filesData["controller"],"r") as controllersFile:
            controllersRawData: dict = json.load(controllersFile)
            self.controllersData = {}
            for key,values in controllersRawData.items():
                self.controllersData.update({
                    key: {
                        "name": values["name"],
                        "value": values["baudrate"]
                    }
                })

        with open(filesData["path"]+filesData["configuration"],"r") as configsFile:
            self.configsData: dict = json.load(configsFile)

    def getAvailablePorts(self):
        self.portsData = {}
        pass

class ModelControl:
    def __init__(self, axis_names):
        self.values = { axis_name:None for axis_name in axis_names } # usually in mm (unit)
        self.speeds = { axis_name:None for axis_name in axis_names } # usually in mm/s (unit/s)
    
    def setValue(self, axis, value):
        self.values.update({ axis:value })

    def setSpeed(self, axis, speed):
        self.speeds.update({ axis:speed })


def inWithStartKeys(value: str, startkeys: list):
    for start_key in startkeys:
        if start_key == value[:len(start_key)]:
            return True
    return False

def removeWithStartKey(dico: dict, startkey: str):
    keys_to_remove = []
    # search for complete keys
    for key in dico.keys():
        if startkey == key[:len(startkey)]:
            keys_to_remove.append(key)
    # remove from dict
    for key_to_remove in keys_to_remove:
        del dico[key_to_remove]
    return dico

if __name__ == "__main__":
    print("start models")

    ms = ModelSettings(('X','Y'))
    ms.loadSettings(config.path)

    sd = ms.getSettingsDict()

    for krsd,vrsd in sd.items(): 
        print(krsd)
        for kkrsd, vvrsd in vrsd.items(): 
            print(kkrsd,vvrsd)