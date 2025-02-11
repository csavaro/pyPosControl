import config
import json
import communications as cmds

class ModelSettings:
    axisParameters = ["platine"]
    
    def __init__(self, axis_names):
        self.axis = axis_names
        # link to controller class for port list
        self.port = None # from available ports
        self.stepscales = { axis_name:None for axis_name in axis_names } # platines
        self.baudrate = None # controller

    def saveSettings(self, path: str, port: str = None, platines: dict = None, controller: str = None):
        with open(path+"settings_files\\save.json","r") as saveFile:
            settingsDict = json.load(saveFile)

        platinesDict = { "platine"+axis:value for axis,value in platines.items() }
        settingsDict["settings"].update(platinesDict)
        settingsDict["settings"].update({
            "controller": controller,
            "port": port
        })

        with open(path+"settings_files\\save.json","w") as saveFile:
            json.dump(settingsDict, saveFile, indent=4)

        # Apply saved settings
        print("applying settings")
        stepscales_dict = {} 
        for keyAxis,valStepScale in self.settingsData.items():
            if "stepscale" in keyAxis and keyAxis[9:] in self.axis:
                stepscales_dict.update({
                    keyAxis[9:]:
                    float(self.platinesData[valStepScale]["value"])
                })
        if (self.settingsData["controller"]):
            baudrate = self.controllersData[self.settingsData["controller"]]["value"]
        else:
            baudrate = 0
        self.applySettings(
            port=self.settingsData["port"], 
            stepscales=stepscales_dict, 
            baudrate=baudrate
        )

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
            print(isAxisRel,paramName)
            if inWithStartKeys(keySett, self.axisParameters) and isAxisRel:
                # print("AXIS REL",keySett)
                if paramName == "platine":
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
                elif keySett == "controller":
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
                        "name": key,
                        "value": values["stepscale"]
                    }
                })

        with open(filesData["path"]+filesData["controller"],"r") as controllersFile:
            controllersRawData: dict = json.load(controllersFile)
            self.controllersData = {}
            for key,values in controllersRawData.items():
                self.controllersData.update({
                    key: {
                        "name": key,
                        "value": values["baudrate"]
                    }
                })

        with open(filesData["path"]+filesData["configuration"],"r") as configsFile:
            self.configsData: dict = json.load(configsFile)

        # Apply saved settings
        print("applying settings")
        stepscales_dict = {} 
        for keyAxis,valPlatine in self.settingsData.items():
            if "platine" in keyAxis and keyAxis[len("platine"):] in self.axis:
                stepscales_dict.update({
                    keyAxis[len("platine"):]:
                    float(self.platinesData[valPlatine]["value"])
                })
        if (self.settingsData["controller"]):
            baudrate = self.controllersData[self.settingsData["controller"]]["value"]
        else:
            baudrate = 0
        self.applySettings(
            port=self.settingsData["port"], 
            stepscales=stepscales_dict, 
            baudrate=baudrate
        )
    
    def getAvailablePorts(self):
        self.portsData = {}
        pass

class ModelControl:
    def __init__(self, axis_names, communication: cmds.Commands = None, settings: ModelSettings = None):
        self.values = { axis_name:0 for axis_name in axis_names } # usually in mm (unit)
        self.speeds = { axis_name:0 for axis_name in axis_names } # usually in mm/s (unit/s)
        self.settings = settings

        self.communication = communication
    
    def setValue(self, axis, value):
        self.values.update({ axis:value })

    def setSpeed(self, axis, speed):
        self.speeds.update({ axis:speed })

    def convertMmToSteps(self, axis_values: dict):
        for axis,value in axis_values.items():
            print("val:",value," - stepscale:",self.settings.stepscales[axis])
            axis_values[axis] = value * self.settings.stepscales[axis]
        return axis_values

    def incrMove(self, axis_values: dict, axis_speeds: dict = None):
        axis_values = self.convertMmToSteps(axis_values)
        axis_speeds = self.convertMmToSteps(axis_speeds)
        # Create and execute command
        cmd = self.communication.moveCmd(axis_values=axis_values, axis_speeds=axis_speeds)
        print("sending ",cmd)
        # Deduce current value
        for key,incrVal in axis_values.items():
            if axis_speeds[key] > 0:
                self.values[key] += incrVal / self.settings.stepscales[key]
        print("curr pos: ",self.values)
        return cmd

    def absMove(self, axis_values: dict, axis_speeds: dict = None):
        # Transform absolute values to relative values
        rel_axis_values = axis_values.copy()
        for key,val in axis_values.items():
            rel_axis_values[key] = -(self.values[key]-val)
        print("mmmmmmmh",rel_axis_values)

        rel_axis_values = self.convertMmToSteps(rel_axis_values)
        axis_speeds = self.convertMmToSteps(axis_speeds)
        print(rel_axis_values)
        # Create and execute command
        cmd = self.communication.moveCmd(axis_values=rel_axis_values, axis_speeds=axis_speeds)
        print("sending ",cmd)
        # Deduce current value
        for key,absVal in axis_values.items():
            if axis_speeds[key] > 0:
                self.values[key] = absVal #/ self.settings.stepscales[key]
        print("curr pos: ",self.values)
        return cmd

    def stop(self):
        cmd = self.communication.stopCmd()
        print("sending ",cmd)
        return cmd

    def goZero(self):
        # Getting axis delta to go to zero
        axis_values = {}
        axis_speeds = {}
        for axis,curPos in self.values.items():
            axis_values.update({
                axis: -curPos
            })
            axis_speeds.update({
                axis: 500
            })
        # Create and execute command
        cmd = self.communication.moveCmd(axis_values=axis_values,axis_speeds=axis_speeds)
        print("go zero ",cmd)
        # Update current position values
        for axis in self.values.keys(): self.values[axis] = 0
        return cmd
    
    def setZero(self):
        for axis in self.values.keys(): self.values[axis] = 0
        print("set as zero")


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

    ms.saveSettings(config.path, port="COM2", controller="Controller 3", platines={
        "X": "Platine 3",
        "Y": "Platine 3"
    })

    # sd = ms.getSettingsDict()

    # for krsd,vrsd in sd.items(): 
    #     print(krsd)
    #     for kkrsd, vvrsd in vrsd.items(): 
    #         print(kkrsd,vvrsd)