import json
import python_files.communications as com
import python_files.connection as co
from threading import Thread,Lock
import time
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)


class ModelSettings:
    """
    Load, store and update settings to send the signal.
    """
    axisParameters = ["platine"]
    
    def __init__(self, axis_names : tuple, wait_ack : bool = True):
        """
        :param axis_names: list of axis names, up to 3 axis implemented
        :type axis_names: tuple, list
        """
        self.axis = axis_names
        # link to controller class for port list
        self.port: str = None # from available ports
        self.stepscales: dict = { axis_name:None for axis_name in axis_names } # platines
        self.speed_limits: dict = { axis_name:{ "max":None, "min":None } for axis_name in axis_names } # platines
        self.baudrate: int = None # controller

        self.default_speeds: dict = { axis_name:None for axis_name in axis_names } # default speed values

        self.connection: co.SerialConnection = co.SerialConnection(wait_ack=wait_ack) # connection to controller

        # Ports data
        self.portsData = self.getAvailablePorts()

    def saveSettings(self, path: str, port: str = None, platines: dict = None, controller: str = None):
        """
        Save and apply settings in parameters and current into json files.

        :param path: absolute path of the current app files, will be used to look at `$\\settings_files\\save.json`
        :type path: str
        :param port: *(Optional)* computer port to communicate with the controller. *ex: `'COM3'`*
        :type port: str
        :param platines: *(Optional)* platines settings as a dict with key as axis. *ex: `{ 'x':"Platine Name" }`*
        :type platines: dict[str:str]
        :param controller: *(Optional)* controller name to communicate with.
        :type controller: str
        """
        with open(path+"settings_files\\save.json","r") as saveFile:
            settingsDict = json.load(saveFile)

        if platines != None:
            platinesDict = { "platine"+axis:value for axis,value in platines.items() }
            settingsDict["settings"].update(platinesDict)
        if controller != None:
            settingsDict["settings"].update({
                "controller": controller
            })
        if port != None:
            settingsDict["settings"].update({
                "port": port
            })

        with open(path+"settings_files\\save.json","w") as saveFile:
            json.dump(settingsDict, saveFile, indent=4)

        # Apply saved settings
        # print("saving settings")
        logger.info("saving settings")
        stepscales_dict = {} 
        speed_limits_dict = {}
        if (platines != None):
            for axis,valPlatine in platines.items():
                if valPlatine:
                    stepscales_dict.update({
                        axis:
                        float(self.platinesData[valPlatine]["value"])
                    })
                    speed_limits_dict.update({
                        axis: {
                            "max": self.platinesData[valPlatine]["max_speed"],
                            "min": self.platinesData[valPlatine]["min_speed"]
                        }
                    })
                else:
                    stepscales_dict.update({
                        axis:
                        0
                    })
                    speed_limits_dict.update({
                        axis: {
                            "max": 0,
                            "min": 0
                        }
                    })

        if (controller):
            baudrate = self.controllersData[controller]["value"]
            communication = self.controllersData[controller]["communication"]
        else:
            baudrate = 0
            communication = -1

        # Disgusting but should works, to change later
        if port == None:
            port = -1
        if stepscales_dict == None:
            stepscales_dict = -1
        if speed_limits_dict == None:
            speed_limits_dict = -1
        if controller == None:
            baudrate = -1
            communication = -1

        self.applySettings(
            port=port, 
            stepscales=stepscales_dict,
            speed_limits=speed_limits_dict, 
            baudrate=baudrate,
            communication=communication
        )

    def applySettings(self, port: str = -1, stepscales: dict = -1, speed_limits: dict = -1, baudrate: int = -1, communication: str = -1):
        """
        Apply concrete settings from parameters to model properties

        :param port: *(Optional)* computer port to communicate with the controller. *ex: `'COM3'`*
        :type port: str
        :param stepscales: *(Optional)* stepscale of platines in `step/mm` unit by axis as key used to convert input to command. *ex: `{ 'x':500 }`*
        :type stepscales: dict[str:int]
        :param speed_limits: *(Optional)* speed limits in `mm/s` unit by axis as key used to secure speed in commands. *ex: `{ 'x':50 }`*
        :type speed_limits: dict[str:int]
        :param baudrate: *(Optional)* baudrate in `baud/s` unit to communicate with the controller.
        :type baudrate: int
        :param communication: *(Optional)* language of commands to communicate with the controller.
        :type communication: str
        """
        if port != -1: # and port in self.portsData ?
            # print(f"ModelSetting: setting port as {port}")
            logger.debug(f"ModelSetting: setting port as {port}")
            if(not isinstance(port,str)):
                raise TypeError(f"port should be a string, not {type(port)} [value:{port}]")
            self.port = port
            self.connection.port = self.port
        if stepscales != -1:
            for keyAxis,valStepScale in stepscales.items():
                if keyAxis in self.stepscales.keys(): # and valStepScale in self.platinesData ?
                    if(not isinstance(valStepScale,(float,int))):
                       raise TypeError(f"stepscales values should be float or int, not {type(valStepScale)} [value:{valStepScale}]")
                    # print(f"ModelSetting: setting stepscale on {keyAxis} axis as {valStepScale}")
                    logger.debug(f"ModelSetting: setting stepscale on {keyAxis} axis as {valStepScale}")
                    self.stepscales.update({
                        keyAxis: valStepScale
                    })
        if speed_limits != -1:
            for keyAxis,valLimit in speed_limits.items():
                valLimit: dict
                if keyAxis in self.speed_limits.keys():
                    if((valLimit["max"] and not isinstance(valLimit["max"],(float,int))) or (valLimit["min"] and not isinstance(valLimit["min"],(float,int,None)))):
                        raise TypeError(f"speed limits should be float or int, not {type(valLimit)} [value:{valLimit}]")
                    # print(f"ModelSetting: setting speed limits on {keyAxis} axis as {valLimit}")
                    logger.debug(f"ModelSetting: setting speed limits on {keyAxis} axis as {valLimit}")
                    self.speed_limits.update({
                        keyAxis: {
                            "max": valLimit["max"],
                            "min": valLimit["min"]
                        }
                    })
                    
        if baudrate != -1: # and baudrate in self.controllersData ?
            if(not isinstance(baudrate,int)):
                # print(f"baudrate should be an int, not {type(baudrate)} [value:{baudrate}]")
                logger.warning(f"baudrate should be an int, not {type(baudrate)} [value:{baudrate}]")
            # print(f"ModelSetting: setting baudrate as {baudrate}")
            logger.debug(f"ModelSetting: setting baudrate as {baudrate}")
            self.baudrate = baudrate
            self.connection.baudrate = self.baudrate

        if communication != -1:
            if(not isinstance(communication,str)):
                logger.warning(f"communication should be a str, not {type(communication)} [value:{communication}]")
            logger.debug(f"ModelSetting: setting communication as {communication}")
            self.communication = com.getCommandsClass(communication, self.default_speeds)

    def applySettingsFromData(self):
        """
        Apply concrete settings from values in self.settingsData dictionary;
        """
        # Apply saved settings
        # print("applying settings")
        logger.info("applying settings")
        stepscales_dict = {}
        speed_limits_dict = {} 
        for keyAxis,valPlatine in self.settingsData.items():
            if "platine" in keyAxis and keyAxis[len("platine"):] in self.axis:
                if valPlatine:
                    stepscales_dict.update({
                        keyAxis[len("platine"):]:
                        float(self.platinesData[valPlatine]["value"])
                    })
                    speed_limits_dict.update({
                        keyAxis[len("platine"):]: {
                            "max": self.platinesData[valPlatine]["max_speed"],
                            "min": self.platinesData[valPlatine]["min_speed"]
                        }
                    })
                else:
                    stepscales_dict.update({
                        keyAxis[len("platine"):]:
                        0
                    })
                    speed_limits_dict.update({
                        keyAxis[len("platine"):]: {
                            "max": 0,
                            "min": 0
                        }
                    })
        if (self.settingsData["controller"]):
            baudrate = self.controllersData[self.settingsData["controller"]]["value"]
            communication = self.controllersData[self.settingsData["controller"]]["communication"]
        else:
            baudrate = 0
        self.applySettings(
            port=self.settingsData["port"], 
            stepscales=stepscales_dict,
            speed_limits=speed_limits_dict, 
            baudrate=baudrate,
            communication=communication
        )

    def getSettingsDict(self)->dict:
        """
        Returns a python dictionary with current settings.
        
        The dictionary is organized like :

        ```python
        {
            "parameters": {
                "platineX": {
                    "name": "Platine X",
                    "unit": "step/mm",
                    "default": "Platine 1",
                    "options": {
                        #*other linear turntables/platines in self.platinesData*
                    }
                },
                "port": {
                    "name": "Port",
                    "default": "COM3",
                    "options": {
                        #*other ports in self.portsData*
                    }
                },
                "controller": {
                    "name": "Controller",
                    "unit": "baud/s",
                    "default": "Controller 1",
                    "options": {
                        #*other controllers in self.controllersData*
                    }
                }
            },
            "configs": {
                "Config 1": {
                    "platineX": "Platine 1",
                    "port": "COM3",
                    "controller": "Controller 1"
                }
            }
        }
        ``` 
        """
        settingDico = {
            "parameters": {},
            "configs": {}
        }
        # Parameters
        self.settingsData: dict
        for keySett,valSett in self.settingsData.items():
            isAxisRel,paramName = self.isAxisRelated(keySett)
            # print(isAxisRel,paramName)
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
                            "options": self.portsData
                            # "options": {
                            #     "COM1": { "name": "COM1", "value": "COM1"},
                            #     "COM3": { "name": "COM3", "value": "COM3"}
                            # }
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

    def isAxisRelated(self, data: str)->tuple[bool,str]:
        """
        Check if an axis name is at the end of a string.

        :param data: data that will be look at
        :type data: str
        :return: Returns firstly a boolean value if end of data string is in self.axis. Second return value is the axis name if found, empty string otherwise.
        :rtype: tuple[bool,str]
        """
        for oneAxis in self.axis:
            if oneAxis == data[-len(oneAxis):]:
                return True,data[:-len(oneAxis)]
        return False,""

    def loadSettings(self, path):
        """
        Load settings from a json file into self.saveData, self.defaultData, self.platinesData, self.controllersData and self.configsData properties.
        Will load settings_files\\save.json file and then controller, platines and config files specified in the save.json file.
        
        :param path: current path of the app files, will try to load the settings file at **path\\settings_files\\save.json**
        :type path: str
        """
        # Saved data
        with open(path+"settings_files\\save.json","r") as saveFile:
            saveData = json.load(saveFile)
            filesData = saveData["files"]
            self.settingsData = saveData["settings"]
            self.defaultData = saveData["default"]

        splitted_path = filesData["path"].split("\\")
        if "current" in splitted_path and "current" == splitted_path[0]:
            splitted_path[0] = path
            filesData["path"] = "\\".join(splitted_path)

        # Platines data
        with open(filesData["path"]+filesData["platine"],"r") as platinesFile:
            platinesRawData: dict = json.load(platinesFile)
            self.platinesData = {}
            for key,values in platinesRawData.items():
                values: dict
                max_speed = None
                min_speed = None
                if "vmax" in values.keys():
                    max_speed = values["vmax"]
                if "vmin" in values.keys():
                    min_speed = values["vmin"]
                self.platinesData.update({
                    key: {
                        "name": key,
                        "value": values["stepscale"],
                        "max_speed": max_speed,
                        "min_speed": min_speed
                    }
                })

        # Controller data
        with open(filesData["path"]+filesData["controller"],"r") as controllersFile:
            controllersRawData: dict = json.load(controllersFile)
            self.controllersData = {}
            for key,values in controllersRawData.items():
                self.controllersData.update({
                    key: {
                        "name": key,
                        "value": values["baudrate"],
                        "communication": values["communication"]
                    }
                })

        # Configs data
        with open(filesData["path"]+filesData["configuration"],"r") as configsFile:
            self.configsData: dict = json.load(configsFile)

        # Ports data
        # Take too much time
        # self.portsData = self.getAvailablePorts()

    def applyDefault(self):
        """
        Apply current settings with the current default values loaded in self.defaultData.
        """
        self.defaultData: dict
        for key,defData in self.defaultData.items():
            arel,pname = self.isAxisRelated(key)
            if arel and pname == "speed":
                self.default_speeds[key[len(pname):]] = defData

    def getAvailablePorts(self):
        """
        Read available ports from pyserial.Serial.
        Returns format is like : { "COM3": { "name": "COM3", "value": "COM3" } }

        :return: dictionary of available ports 
        :rtype: dict[dict]
        """
        # return {
        #     "COM1": { "name": "COM1", "value": "COM1"},
        #     "COM2": { "name": "COM2", "value": "COM2"},
        #     "COM3": { "name": "COM3", "value": "COM3"},
        #     "COM4": { "name": "COM4", "value": "COM4"}
        # }
        return { port: { "name": port, "value": port } for port in self.connection.available_serial_ports() }

class ModelControl:
    """
    Core class of this project.

    Launch commands, save current position, read settings from python_files.models.ModelSettings and save concrete settings.
    Every actions is managed by this class.
    """
    def __init__(self, axis_names, settings: ModelSettings = None):
        """
        :param axis_names: axis names like ('X','Y'). Up to 3 axis supported.
        :type axis_names: tuple | list
        :param communication: concrete Commands class instance for the commands format.
        :type communication: python_files.communications.Commands
        :param settings: settings class to get values from
        :type settings: python_files.models.ModelSettings 
        """
        self.values     = { axis_name:0 for axis_name in axis_names } # usually in mm (unit)
        self.speeds     = { axis_name:0 for axis_name in axis_names } # usually in mm/s (unit/s)
        self.settings = settings

        self.connection = self.settings.connection # controller connection

        # self.teCommands = None
        self.teCommands = ThreadExecutor("SerialConnectionThreadList")

        self.teCommands.start()
    
    def setValue(self, axis, value):
        """
        Set current position value on the specified axis. Unit is mm.

        :param axis: axis name
        :type axis: str
        :param value: position/movement value (mm)
        :type value: float | int
        """
        self.values.update({ axis:value })

    def setSpeed(self, axis, speed):
        """
        Set speed value on the specified axis. Unit is mm/s.

        :param axis: axis name
        :type axis: str
        :param speed: speed value (mm/s)
        :type speed: float | int
        """
        self.speeds.update({ axis:speed })

    def calcMoveTime(self, axis_values: dict, axis_speeds: dict, bonus_time = 1)->float:
        """
        Calculate the time expected to move from position 0 to axis_values position at axis_speeds speed.
        Bonus is additional time (s).

        :param axis_values: position values  for each axis formatted like { 'X': 50 }. Unit is mm
        :type axis_values: dict[str:int|float]
        :param axis_speeds: speed values  for each axis formatted like { 'X': 5 }. Unit is mm/s
        :type axis_speeds: dict[str:int|float]
        :param bonus_time: additional time (s).
        :type bonus_time: float | int
        :return: time expected to take to move to specified position from a position 0. Unit is s
        :rtype: float | int
        """
        dtimes = []
        for axis in axis_values.keys():
            if axis_speeds[axis] != 0:
                dtimes.append(abs(axis_values[axis])/axis_speeds[axis])
        t = max(dtimes)+bonus_time
        # print(f"movement time is expected to be {t} (with {bonus_time} bonus time)")
        logger.debug(f"movement time is expected to be {t} (with {bonus_time} bonus time)")
        return t


    def convertMmToSteps(self, axis_values: dict):
        """
        Converts position values from mm to step units according to stepscale in self.settings.stepscales

        :param axis_values: position values  for each axis formatted like { 'X': 50 }. Unit is mm
        :type axis_values: dict[str:int|float]
        :return: axis_values converted from mm to step units
        :rtype: dict[str:int]
        """
        axis_values = deepcopy(axis_values)
        for axis,value in axis_values.items():
            # print("val:",value," - stepscale:",self.settings.stepscales[axis])
            axis_values[axis] = value * self.settings.stepscales[axis]
        return axis_values
    
    def checkSpeed(self, axis_speeds: dict):
        """
        check if axis_speed values are within the limits set in the ModelSettings linked.

        :param axis_speeds: speed values for each axis formatted like { 'X': 5 }. Unit is mm/s
        :type axis_speeds: dict[str:int|float]
        :return: axis_speed with speed limit as value if axis_speed values are not in range.
        :rtype: dict[str:float|int]
        """
        for axis,speed in axis_speeds.items():
            smax = self.settings.speed_limits[axis]["max"]
            smin = self.settings.speed_limits[axis]["min"]
            if smax and speed > smax:
                axis_speeds[axis] = smax
            elif smin and speed < smin:
                axis_speeds[axis] = smin
        return axis_speeds

    def incrMove(self, axis_values: dict, axis_speeds: dict = None, callbacks: list = None, miss_val_cbs: list = None, finally_cbs: list = None):
        """
        launch a command to move to axis_values without taking on board current position.

        :param axis_values: position values to move to for each axis. Formatted like { 'X': 50 }. Unit is mm
        :type axis_values: dict[str:int|float]
        :param axis_speeds: speed values for each axis formatted like { 'X': 5 }. Unit is mm/s
        :type axis_speeds: dict[str:int|float]
        :param callbacks: actions to do at the end of the movement
        :type callbacks: list[function]
        :param: miss_val_cbs: actions to do if a python_files.connection.MissingValue exception is raised during the movement and the callbacks
        :type miss_val_cbs: list[function]
        :param finally_cbs: actions to do after the movement in a finally statement
        :type finally_cbs: list[function]
        :return: command(s) sent to controller
        :rtype: str
        """
        axis_speeds = self.checkSpeed(axis_speeds)
        axis_values = self.convertMmToSteps(axis_values)
        axis_speeds = self.convertMmToSteps(axis_speeds)
        # Create and execute command
        cmds = self.settings.communication.moveCmd(axis_values=axis_values, axis_speeds=axis_speeds)
        # res = self.connection.executeSelfCmd(cmds)
        # res = self.teCommands.addTask(self.connection.executeSelfCmd, cmds)

        tth = Thread(target=time.sleep,args=(self.calcMoveTime(axis_values,axis_speeds),))

        functionList = []
        functionList.append(tth.start)
        functionList.append(lambda c=cmds: self.connection.executeSelfCmd(c))
        functionList.append(tth.join)
        # functionList.append(lambda t=self.calcMoveTime(axis_values,axis_speeds): time.sleep(t))
        functionList.append(lambda axv=axis_values,axs=axis_speeds: self.incrUpdate(axv,axs))
        if callbacks:
            functionList += callbacks
        logger.info(f"sending incremental move to {axis_values}")
        res = self.teCommands.addTask(lambda fl=functionList,mv=miss_val_cbs,fcb=finally_cbs: functionPackage(fl,mv,fcb))

        # time.sleep(1)

        # print("DO SMTH?",res)
        # if res == 0:
        #     # Deduce current value
        #     for key,incrVal in axis_values.items():
        #         if axis_speeds[key] > 0:
        #             self.values[key] += incrVal / self.settings.stepscales[key]
        
        # print("curr pos: ",self.values)
        return self.settings.communication.commandsToString(cmds)


    def absMove(self, axis_values: dict, axis_speeds: dict = None, callbacks: list = None, miss_val_cbs: list = None, finally_cbs: list = None):
        """
        launch a command to move to axis_values from current position values.

        :param axis_values: position values to move to for each axis. Formatted like { 'X': 50 }. Unit is mm
        :type axis_values: dict[str:int|float]
        :param axis_speeds: speed values for each axis formatted like { 'X': 5 }. Unit is mm/s
        :type axis_speeds: dict[str:int|float]
        :param callbacks: actions to do at the end of the movement
        :type callbacks: list[function]
        :param: miss_val_cbs: actions to do if a python_files.connection.MissingValue exception is raised during the movement and the callbacks
        :type miss_val_cbs: list[function]
        :param finally_cbs: actions to do after the movement in a finally statement
        :type finally_cbs: list[function]
        :return: command(s) sent to controller
        :rtype: str
        """
        # Transform absolute values to relative values
        rel_axis_values = axis_values.copy()
        for key,val in axis_values.items():
            rel_axis_values[key] = -(self.values[key]-val)

        axis_speeds = self.checkSpeed(axis_speeds)
        rel_axis_values = self.convertMmToSteps(rel_axis_values)
        axis_speeds = self.convertMmToSteps(axis_speeds)
        # print(rel_axis_values)

        # Create and execute command
        cmds = self.settings.communication.moveCmd(axis_values=rel_axis_values, axis_speeds=axis_speeds)
        # print("sending ",cmds)
        # res = self.connection.executeSelfCmd(cmds)
        # res = self.teCommands.addTask(self.connection.executeSelfCmd, cmds)

        tth = Thread(target=time.sleep,args=(self.calcMoveTime(rel_axis_values,axis_speeds),))

        functionList = []
        functionList.append(tth.start)
        functionList.append(lambda c=cmds: self.connection.executeSelfCmd(c))
        # functionList.append(lambda t=self.calcMoveTime(rel_axis_values,axis_speeds): time.sleep(t))
        functionList.append(tth.join)
        functionList.append(lambda axv=axis_values,axs=axis_speeds: self.absUpdate(axv,axs))
        if callbacks:
            functionList += callbacks
        logger.info(f"sending absolute move to {axis_values}")
        res = self.teCommands.addTask(lambda fl=functionList,mv=miss_val_cbs,fcb=finally_cbs: functionPackage(fl,mv,fcb))
        

        # if res:
        #     # Deduce current value
        #     for key,absVal in axis_values.items():
        #         if axis_speeds[key] > 0:
        #             self.values[key] = absVal #/ self.settings.stepscales[key]

        # print("curr pos: ",self.values)
        return self.settings.communication.commandsToString(cmds)

    def stop(self):
        """
        launch a command to stop the controller in it's task.

        :return: command(s) sent to controller
        :rtype: str
        """
        cmds = self.settings.communication.stopCmd()
        # print("sending ",cmd)
        logger.info("sending stop")
        Thread(target=self.connection.executeSelfCmd, args=(cmds,)).start()

        return 0
        return self.settings.communication.commandsToString(cmds)

    def goZero(self, callbacks: list = None, miss_val_cbs: list = None, finally_cbs: list = None):
        """
        launch a move command to controller to go position 0 on each axis from the current position values.
        Speed of the movement is either mid value between max and min, or max/2 if no min, or min*2 if no max, 5mm/s instead.

        :param callbacks: actions to do at the end of the movement
        :type callbacks: list[function]
        :param: miss_val_cbs: actions to do if a python_files.connection.MissingValue exception is raised during the movement and the callbacks
        :type miss_val_cbs: list[function]
        :param finally_cbs: actions to do after the movement in a finally statement
        :type finally_cbs: list[function]
        :return: command(s) sent to controller
        :rtype: str
        """
        # Getting axis delta to go to zero
        axis_values = {}
        axis_speeds = {}
        for axis,curPos in self.values.items():
            smax = self.settings.speed_limits[axis]["max"]
            smin = self.settings.speed_limits[axis]["min"]
            speed = 5
            if smax and smin and smax-smin>0:
                speed = (smin+smax)/2
            elif smax and smax>0:
                speed = smax/2
            elif smin and smin>0:
                speed = smin*2
            axis_values.update({
                axis: -curPos
            })
            axis_speeds.update({
                axis: speed
            })
        axis_values = self.convertMmToSteps(axis_values)
        axis_speeds = self.convertMmToSteps(axis_speeds)

        # Create and execute command
        cmds = self.settings.communication.moveCmd(axis_values=axis_values,axis_speeds=axis_speeds)
        # print("go zero ",cmds)
        # res = self.connection.executeSelfCmd(cmds)
        # res = self.teCommands.addTask(self.connection.executeSelfCmd, cmds)

        tth = Thread(target=time.sleep,args=(self.calcMoveTime(axis_values,axis_speeds),))

        functionList = []
        functionList.append(tth.start)
        functionList.append(lambda c=cmds: self.connection.executeSelfCmd(c))
        # functionList.append(lambda t=self.calcMoveTime(axis_values,axis_speeds): time.sleep(t))
        functionList.append(tth.join)
        functionList.append(self.zeroUpdate)
        if callbacks:
            functionList += callbacks
        logger.info("sending go to zero")
        res = self.teCommands.addTask(lambda fl=functionList,mv=miss_val_cbs,fcb=finally_cbs: functionPackage(fl,mv,fcb))

        # if res:
        #     # Update current position values
        #     for axis in self.values.keys(): self.values[axis] = 0

        return self.settings.communication.commandsToString(cmds)
    
    def setZero(self):
        """
        Set current position values as zero on each axis without moving or sending a command to controller.
        """
        for axis in self.values.keys(): self.values[axis] = 0
        # print("set as zero")
        logger.info("current position set as zero")

    def goHome(self, callbacks: list = None, miss_val_cbs: list = None, finally_cbs: list = None):
        """
        Set current position as home on the controller.
        
        :return: command(s) sent to controller
        :rtype: str
        """
        # functionList = []
        # functionList.append(lambda c=self.settings.communication.goHome: self.connection.executeSelfCmd(c))
        # if callbacks:
        #     functionList += callbacks
        # res = self.teCommands.addTask(lambda fl=functionList,mv=miss_val_cbs,fcb=finally_cbs: functionPackage(fl,mv,fcb))

        cmds = self.settings.communication.goHome(len(self.settings.axis))
        # print("sending ",cmd)
        logger.info("sending go home")
        self.connection.executeSelfCmd(cmds)
        return self.settings.communication.commandsToString(cmds)


    def setHome(self, callbacks: list = None, miss_val_cbs: list = None, finally_cbs: list = None):
        """
        Go to current home position on the controller.
        
        :return: command(s) sent to controller
        :rtype: str
        """
        # functionList = []
        # functionList.append(lambda c=self.settings.communication.setHome: self.connection.executeSelfCmd(c))
        # if callbacks:
        #     functionList += callbacks
        # res = self.teCommands.addTask(lambda fl=functionList,mv=miss_val_cbs,fcb=finally_cbs: functionPackage(fl,mv,fcb))

        cmds = self.settings.communication.setHome(len(self.settings.axis))
        # print("sending ",cmd)
        logger.info("sending set home")
        self.connection.executeSelfCmd(cmds)
        return self.settings.communication.commandsToString(cmds)


    def rawAction(self, commands: list[str], callbacks: list = None, miss_val_cbs: list = None, finally_cbs: list = None):
        """
        Send list of commands converted in ascii into the serial connection.
        
        :return: command(s) sent to controller
        :rtype: str
        """
        cmds = []
        for cmd in commands:
            cmds.append(cmd.encode("ascii"))

        functionList = []
        functionList.append(lambda c=cmds: self.connection.executeSelfCmd(c))
        if callbacks:
            functionList += callbacks
        logger.info("sending raw commands")
        res = self.teCommands.addTask(lambda fl=functionList,mv=miss_val_cbs,fcb=finally_cbs: functionPackage(fl,mv,fcb))

        return "\n".join(commands)

    def incrUpdate(self, axis_values: dict, axis_speeds: dict):
        """
        Update current position values after a incremental movement to the set of positions specified.

        :param axis_values: position values to move to for each axis. Formatted like { 'X': 50 }. Unit is mm
        :type axis_values: dict[str:int|float]
        :param axis_speeds: speed values for each axis formatted like { 'X': 5 }. Unit is mm/s
        :type axis_speeds: dict[str:int|float]
        """
        # Deduce current value
        for key,incrVal in axis_values.items():
            if axis_speeds[key] > 0:
                self.values[key] += incrVal / self.settings.stepscales[key]

    def absUpdate(self, axis_values: dict, axis_speeds: dict):
        """
        Update current position values after an absolute movement to the set of positions specified.

        :param axis_values: position values to move to for each axis. Formatted like { 'X': 50 }. Unit is mm
        :type axis_values: dict[str:int|float]
        :param axis_speeds: speed values for each axis formatted like { 'X': 5 }. Unit is mm/s
        :type axis_speeds: dict[str:int|float]
        """
        # Deduce current value
        for key,absVal in axis_values.items():
            if axis_speeds[key] > 0:
                self.values[key] = absVal #/ self.settings.stepscales[key]

    def zeroUpdate(self):
        """
        Update current position values to position 0.
        """
        for axis in self.values.keys(): self.values[axis] = 0

    def quit(self):
        """
        Close and kill the thread waiting list used to execute actions like movements.
        
        Meant to be executed at the end of the program.
        """
        if isinstance(self.teCommands,ThreadExecutor):
            self.connection.close()
            self.teCommands.kill()


def inWithStartKeys(value: str, startkeys: list):
    """
    Returns if a start key has been found at the beginning of the value.

    :param value: value to be check if a start key is in
    :type value: str
    :param startkeys: start keys to check inside value
    :type startkeys: list[str]
    :return: a start key has been found in value
    :rtype: boolean
    """
    for start_key in startkeys:
        if start_key == value[:len(start_key)]:
            return True
    return False

def removeWithStartKey(dico: dict, startkey: str):
    """
    Remove the beginning of dico keys if startkey has been found.

    :param dico: dictionary without startkey in it's keys
    :type dico: dict[str:]
    :param startkey: start key to remove in the dico
    :type startkey: str
    :return: dico without startkey in it's keys
    :rtype: dict[str:]
    """
    keys_to_remove = []
    # search for complete keys
    for key in dico.keys():
        if startkey == key[:len(startkey)]:
            keys_to_remove.append(key)
    # remove from dict
    for key_to_remove in keys_to_remove:
        del dico[key_to_remove]
    return dico

class ThreadExecutor(Thread):
    """
    Thread waiting list.

    wait_list_size is a static parameter.
    """
    wait_list_size: int = 1

    def __init__(self, name: str):
        """
        :param name: ThreadExecutor name shown in logger messages
        :type name: str
        """
        Thread.__init__(self)
        self.curr_thread: Thread = None
        self.wait_list  : list   = []
        self._lock      : Lock   = Lock()
        self.name       : str    = name
        self.killed     : bool   = False
        self.interval_time : int = 0.5  # seconds

    def run(self):
        """
        Run until killed. Run tasks from it's waiting list.
        """
        # counter = 0

        while not self.killed:
            # affichages
            time.sleep(self.interval_time)
            #print("\n" + self.name + "\t" + str(counter) + "s")
            # print(self.curr_thread)
            # print(self.wait_list)
            # counter += interval_time

            # gestion concrete
            if self.wait_list:
                # si liste non vide
                with self._lock:
                    # assignation du thread courant
                    self.curr_thread = self.wait_list.pop(0)
                # lancement du thread courant
                self.curr_thread.start()
                # attente de la fin du thread courant
                self.curr_thread.join()
                # suppression du thread courant execute
                self.curr_thread = None
        # print(self.name + " has been killed.")
        logger.debug(f"{self.name} has been killed.")

    def addTask(self, newtask, *taskargs):
        """
        Create thread for the new task and add it to the waiting list.

        :return: Added thread if everything went well, 1 if waiting list was full and task not took into account.
        :rtype: Thread | int
        """
        thntask = Thread(target=newtask,args=taskargs)
        ret = self.addThreadedTask(thntask)
        if ret != 0:
            thntask = ret
        return thntask
        # return self.addThreadedTask(thntask)

    # ajout d une tache a la liste d attente a executer
    def addThreadedTask(self, newthread: Thread):
        """
        Add task in a thread to the waiting list if not full.

        :return: 0 if everything went well, 1 if waiting list was full and task not took into account.
        :rtype: int
        """
        # verification de la taille de la liste d attente
        if len(self.wait_list) < self.wait_list_size or (len(self.wait_list)==0 and not self.isRunning()):
            with self._lock:
                # si il reste de la place, ajout a la liste
                self.wait_list.append(newthread)
            return 0
        else:
            # si plus de place, affichage de la non prise en compte de la tache
            # print("/!\ Warning /!\ waiting list is too big, thread dropped :" + str(newthread))
            logger.warning(f"/!\ Warning /!\ waiting list is too big, thread dropped : {str(newthread)}")
            return -1

    def isRunning(self):
        """
        :return: If running or not.
        :rtype: bool
        """
        return self.curr_thread is not None

    def getState(self):
        """
        Return value possibilities:
        - 0 : nothing is running.
        - 1 : one task is running, waiting list is empty.
        - 2 : one task is running, waiting list is full.
        - 3 : one task is running, waiting list has some tasks.
        - 4 : no task is running but waiting list has some tasks.

        :return: state of the ThreadExecutor
        :rtype: int
        """
        if self.curr_thread is None and len(self.wait_list) == 0:
            # nothing running and waiting list is empty
            return 0
        elif self.curr_thread is not None and len(self.wait_list) == 0:
            # one task is running and waiting list is empty
            return 1
        elif self.curr_thread is not None and len(self.wait_list) == self.wait_list_size:
            # one task is running and waiting list is full
            return 2
        elif self.curr_thread is not None and len(self.wait_list) > 0:
            # one task is running and waiting list has some tasks
            return 3
        elif self.curr_thread is None and len(self.wait_list) > 0:
            # nothing is running and waiting list has some tasks
            return 4
        else:
            # nothing recognized
            return 5
        
    # termine le threadexecutor
    def kill(self):
        """
        End the infinite loop of waiting and execute next action.
        Does not interrupt an action.
        """
        self.killed = True


def functionPackage(callbacks: list = None, miss_val_cbs: list = None, finally_cbs: list = None):
    """
    :param callbacks: list of functions to be executed in a try statement
    :type callbacks: list[function]
    :param miss_val_cbs: list of functions to be executed in a except python_files.connection.MissingValue statement.
    :type miss_val_cbs: list[function]
    :param finally_cbs: list of functions to be executed in a finally statement.
    :type finally_cbs: list[function]
    """
    try:
        if callbacks:
            for cb in callbacks:
                if callable(cb):
                    cb()
    except co.MissingValue as e:
        # print("ERROR:",e)
        logger.error(f"ERROR: {e}")
        if miss_val_cbs:
            for mvc in miss_val_cbs:
                if callable(mvc):
                    mvc(e)
    finally:
        if finally_cbs:
            for fcb in finally_cbs:
                if callable(fcb):
                    fcb()

if __name__ == "__main__":
    print("start models")
    # from pathlib import Path
    # path = str(Path(__file__).parent.absolute())+"\\"

    # ms = ModelSettings(('X','Y'))
    # ms.loadSettings(path)

    # ms.saveSettings(path, port="COM2", controller="Controller 3", platines={
    #     "X": "Platine 3",
    #     "Y": "Platine 3"
    # })

    # sd = ms.getSettingsDict()

    # for krsd,vrsd in sd.items(): 
    #     print(krsd)
    #     for kkrsd, vvrsd in vrsd.items(): 
    #         print(kkrsd,vvrsd)