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

    def applySettings(self, port: str = None, stepscales: dict = None, baudrate: int = None):
        """
        Apply settings from parameters in model properties
        """
        if port: # and port in self.portsData ?
            print(f"ModelSetting: setting port as {port}")
            if(not isinstance(port,str)):
                raise TypeError(f"port should be a string, not {type(port)} [value:{port}]")
            self.port = port
        if stepscales:
            for keyAxis,valStepScale in stepscales.items():
                if keyAxis in self.stepscales.keys(): # and valStepScale in self.platinesData ?
                    if(not isinstance(valStepScale,(float,int))):
                       raise TypeError(f"stepscales values should be float or int, not {type(valStepScale)} [value:{valStepScale}]")
                    print(f"ModelSetting: setting stepscale on {keyAxis} axis as {valStepScale}")
                    self.stepscales.update({
                        keyAxis: valStepScale
                    })
        if baudrate: # and baudrate in self.controllersData ?
            if(not isinstance(baudrate,int)):
                print(f"baudrate should be an int, not {type(baudrate)} [value:{baudrate}]")
            print(f"ModelSetting: setting baudrate as {baudrate}")
            self.baudrate = baudrate

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
                # print("AXIS REL",keySett)
                if paramName == "stepscale":
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
                    settingDico["parameters"].update({
                        keySett: {
                            "name": "Port",
                            "default": valSett,
                            # "options": self.portsData
                            "options": {
                                "COM1": { "name": "COM1", "value": "COM1"},
                                "COM3": { "name": "COM3", "value": "COM3"}
                            }
                        }
                    })
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

        # Apply saved settings
        print("applying settings")
        stepscales_dict = {} 
        for keyAxis,valStepScale in self.settingsData.items():
            if "stepscale" in keyAxis and keyAxis[9:] in self.axis:
                stepscales_dict.update({
                    keyAxis[9:]:
                    float(self.platinesData[valStepScale]["value"])
                })
        self.applySettings(
            port=self.settingsData["port"], 
            stepscales=stepscales_dict, 
            baudrate=self.controllersData[self.settingsData["baudrate"]]["value"]
        )
    
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