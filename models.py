import json
import communications as cmds
import connection as co
from threading import Thread,Lock
import time

class ModelSettings:
    axisParameters = ["platine"]
    
    def __init__(self, axis_names):
        self.axis = axis_names
        # link to controller class for port list
        self.port: str = None # from available ports
        self.stepscales: dict = { axis_name:None for axis_name in axis_names } # platines
        self.speed_limits: dict = { axis_name:{ "max":None, "min":None } for axis_name in axis_names } # platines
        self.baudrate: int = None # controller

        self.default_speeds: dict = { axis_name:None for axis_name in axis_names } # default speed values

        self.connection: co.SerialConnection = co.SerialConnection() # connection to controller

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
        speed_limits_dict = {}
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
        else:
            baudrate = 0
        self.applySettings(
            port=port, 
            stepscales=stepscales_dict,
            speed_limits=speed_limits_dict, 
            baudrate=baudrate
        )

    def applySettings(self, port: str = -1, stepscales: dict = -1, speed_limits: dict = -1, baudrate: int = -1):
        """
        Apply settings from parameters in model properties
        """
        if port != -1: # and port in self.portsData ?
            print(f"ModelSetting: setting port as {port}")
            if(not isinstance(port,str)):
                raise TypeError(f"port should be a string, not {type(port)} [value:{port}]")
            self.port = port
            self.connection.port = self.port
        if stepscales != -1:
            for keyAxis,valStepScale in stepscales.items():
                if keyAxis in self.stepscales.keys(): # and valStepScale in self.platinesData ?
                    if(not isinstance(valStepScale,(float,int))):
                       raise TypeError(f"stepscales values should be float or int, not {type(valStepScale)} [value:{valStepScale}]")
                    print(f"ModelSetting: setting stepscale on {keyAxis} axis as {valStepScale}")
                    self.stepscales.update({
                        keyAxis: valStepScale
                    })
        if speed_limits != -1:
            for keyAxis,valLimit in speed_limits.items():
                valLimit: dict
                if keyAxis in self.speed_limits.keys():
                    if((valLimit["max"] and not isinstance(valLimit["max"],(float,int))) or (valLimit["min"] and not isinstance(valLimit["min"],(float,int,None)))):
                        raise TypeError(f"speed limits should be float or int, not {type(valLimit)} [value:{valLimit}]")
                    print(f"ModelSetting: setting speed limits on {keyAxis} axis as {valLimit}")
                    self.speed_limits.update({
                        keyAxis: {
                            "max": valLimit["max"],
                            "min": valLimit["min"]
                        }
                    })
                    
        if baudrate != -1: # and baudrate in self.controllersData ?
            if(not isinstance(baudrate,int)):
                print(f"baudrate should be an int, not {type(baudrate)} [value:{baudrate}]")
            print(f"ModelSetting: setting baudrate as {baudrate}")
            self.baudrate = baudrate
            self.connection.baudrate = self.baudrate

    def applySettingsFromData(self):
        # Apply saved settings
        print("applying settings")
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
        else:
            baudrate = 0
        self.applySettings(
            port=self.settingsData["port"], 
            stepscales=stepscales_dict,
            speed_limits=speed_limits_dict, 
            baudrate=baudrate
        )

    def getSettingsDict(self):
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

    def applyDefault(self):
        self.defaultData: dict
        for key,defData in self.defaultData.items():
            arel,pname = self.isAxisRelated(key)
            if arel and pname == "speed":
                print(f"FOUND SPEED !!! k:{key} - d:{defData}")
                self.default_speeds[key[len(pname):]] = defData

    def getAvailablePorts(self):
        self.portsData = {}
        pass

class ModelControl:
    def __init__(self, axis_names, communication: cmds.Commands = None, settings: ModelSettings = None):
        self.values     = { axis_name:0 for axis_name in axis_names } # usually in mm (unit)
        self.speeds     = { axis_name:0 for axis_name in axis_names } # usually in mm/s (unit/s)
        self.settings = settings

        self.communication = communication # command's language
        self.connection = self.settings.connection # controller connection
        self.teCommands = ThreadExecutor("SerialConnection")
        
        self.teCommands.start()
    
    def setValue(self, axis, value):
        self.values.update({ axis:value })

    def setSpeed(self, axis, speed):
        self.speeds.update({ axis:speed })

    def convertMmToSteps(self, axis_values: dict):
        for axis,value in axis_values.items():
            # print("val:",value," - stepscale:",self.settings.stepscales[axis])
            axis_values[axis] = value * self.settings.stepscales[axis]
        return axis_values
    
    def checkSpeed(self, axis_speeds: dict):
        """
        check if axis_speed values are within the limits set in the ModelSettings linked.
        Parameters:
        - axis_speed: dictionary of str:float|int, speed unit should be mm/s.
        Returns: 
        - same format as axis_speed with speed limit as value if axis_speed values are not in range.
        """
        for axis,speed in axis_speeds.items():
            smax = self.settings.speed_limits[axis]["max"]
            smin = self.settings.speed_limits[axis]["min"]
            if smax and speed > smax:
                axis_speeds[axis] = smax
            elif smin and speed < smin:
                axis_speeds[axis] = smin
        return axis_speeds

    def incrMove(self, axis_values: dict, axis_speeds: dict = None):
        """
        launch a command to move to axis_values without taking on board current position.
        Parameters:
        - axis_values: dict of str:float|int, values on axis to move to. Units should be mm.
        - axis_speeds: dict of str:float|int, speed values on axis. Units should be mm/s.
        Returns:
        - command sent to controller.
        """
        axis_speeds = self.checkSpeed(axis_speeds)
        axis_values = self.convertMmToSteps(axis_values)
        axis_speeds = self.convertMmToSteps(axis_speeds)

        # Create and execute command
        cmds = self.communication.moveCmd(axis_values=axis_values, axis_speeds=axis_speeds)
        print("sending ",cmds)
        # self.connection.executeCmd(cmds)
        res = self.teCommands.addTask(self.connection.executeCmd, cmds)

        if res == 0:
            # Deduce current value
            for key,incrVal in axis_values.items():
                if axis_speeds[key] > 0:
                    self.values[key] += incrVal / self.settings.stepscales[key]
        
        print("curr pos: ",self.values)
        cmds = [cmd.decode("utf-8") for cmd in cmds]
        return "\n".join(cmds)

    def absMove(self, axis_values: dict, axis_speeds: dict = None):
        """
        launch a command to move to axis_values from current position values.
        Parameters:
        - axis_values: dict of str:float|int, values on axis to move to. Units should be mm.
        - axis_speeds: dict of str:float|int, speed values on axis. Units should be mm/s.
        Returns:
        - command sent to controller.
        """
        # Transform absolute values to relative values
        rel_axis_values = axis_values.copy()
        for key,val in axis_values.items():
            rel_axis_values[key] = -(self.values[key]-val)

        axis_speeds = self.checkSpeed(axis_speeds)
        rel_axis_values = self.convertMmToSteps(rel_axis_values)
        axis_speeds = self.convertMmToSteps(axis_speeds)
        print(rel_axis_values)

        # Create and execute command
        cmds = self.communication.moveCmd(axis_values=rel_axis_values, axis_speeds=axis_speeds)
        print("sending ",cmds)
        # self.connection.executeCmd(cmds)
        res = self.teCommands.addTask(self.connection.executeCmd, cmds)

        if res == 0:
            # Deduce current value
            for key,absVal in axis_values.items():
                if axis_speeds[key] > 0:
                    self.values[key] = absVal #/ self.settings.stepscales[key]

        print("curr pos: ",self.values)
        cmds = [cmd.decode("utf-8") for cmd in cmds]
        return "\n".join(cmds)

    def stop(self):
        """
        launch a command to stop the controller in it's task.
        Returns:
        - command sent to controller.
        """
        cmd = self.communication.stopCmd()
        print("sending ",cmd)
        self.connection.executeCmd(cmd)
        return cmd

    def goZero(self):
        """
        launch a move command to controller to go position 0 on each axis from the current position values.
        Speed of the movement is either mid value between max and min, or max/2 if no min, or min*2 if no max, 5mm/s instead.
        Returns:
        - command sent to controller
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
        cmds = self.communication.moveCmd(axis_values=axis_values,axis_speeds=axis_speeds)
        print("go zero ",cmds)
        # self.connection.executeCmd(cmds)
        res = self.teCommands.addTask(self.connection.executeCmd, cmds)

        if res == 0:
            # Update current position values
            for axis in self.values.keys(): self.values[axis] = 0

        cmds = [cmd.decode("utf-8") for cmd in cmds]
        return "\n".join(cmds)
    
    def setZero(self):
        """
        Set current position values as zero on each axis without moving or sending a command to controller.
        """
        for axis in self.values.keys(): self.values[axis] = 0
        print("set as zero")

    def quit(self):
        self.teCommands.kill()


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

class ThreadExecutor(Thread):
    wait_list_size = 3

    def __init__(self, name: str):
        Thread.__init__(self)
        self.curr_thread: Thread = None
        self.wait_list  : list   = []
        self._lock      : Lock   = Lock()
        self.name       : str    = name
        self.killed     : bool   = False

    def run(self):
        """
        Run until killed. Run tasks from it's waiting list.
        """
        # counter = 0
        interval_time = 0.5  # seconds

        while not self.killed:
            # affichages
            time.sleep(interval_time)
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
        print(self.name + " has been killed.")

    def addTask(self, newtask, *taskargs):
        """
        Create thread for the new task and add it to the waiting list.
        Returns:
        - 0 : if everything went well.
        - 1 : if waiting list was full and task not took into account.
        """
        thntask = Thread(target=newtask,args=taskargs)
        return self.addThreadedTask(thntask)

    # ajout d une tache a la liste d attente a executer
    def addThreadedTask(self, newthread: Thread):
        """
        Add task in a thread to the waiting list if not full.
        Returns:
        - 0 : if everything went well.
        - 1 : if waiting list was full and task not took into account.
        """
        # verification de la taille de la liste d attente
        if len(self.wait_list) < self.wait_list_size:
            with self._lock:
                # si il reste de la place, ajout a la liste
                self.wait_list.append(newthread)
            return 0
        else:
            # si plus de place, affichage de la non prise en compte de la tache
            print("/!\ Warning /!\ waiting list is too big, thread dropped :" + str(newthread))
            return -1

    def isRunning(self):
        return self.curr_thread is not None

    def getState(self):
        """
        Return value possibilities:
        - 0 : nothing is running.
        - 1 : one task is running, waiting list is empty.
        - 2 : one task is running, waiting list is full.
        - 3 : one task is running, waiting list has some tasks.
        - 4 : no task is running but waiting list has some tasks.
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
        self.killed = True

if __name__ == "__main__":
    print("start models")
    from pathlib import Path
    path = str(Path(__file__).parent.absolute())+"\\"

    ms = ModelSettings(('X','Y'))
    ms.loadSettings(path)

    ms.saveSettings(path, port="COM2", controller="Controller 3", platines={
        "X": "Platine 3",
        "Y": "Platine 3"
    })

    # sd = ms.getSettingsDict()

    # for krsd,vrsd in sd.items(): 
    #     print(krsd)
    #     for kkrsd, vvrsd in vrsd.items(): 
    #         print(kkrsd,vvrsd)