from ..models import ModelSettings,ModelControl
from ..communications import CSeries
from pathlib import Path
# import csv
from threading import Event
from time import sleep
import pandas as pd
import logging

logger = logging.getLogger(__name__)

path = ""

class MoveAndMeasure:
    """
    Attributes :
    - axis (tuple) : names of axis ex ('x','y','z'). Up to 3 axis supported.
    - roadmap (list[list[str]]) : 2d list of positions loaded.
    - move_finished_event (threading.Event) : event when running, wait until set before doing a measurement.
    - settingsData (dict) : loaded and effective settings.
    """
    def __init__(self, axis_names: tuple):
        self.axis = axis_names

        self.roadmap = None

        self.mSettings = ModelSettings(self.axis)
        self.mSettings.loadSettings(path)
        self.mSettings.applySettingsFromData()
        self.mSettings.applyDefault()
        self.mControl = ModelControl(self.axis, CSeries(axis_speeds=self.mSettings.default_speeds), settings=self.mSettings)

        # self.loadMoveSet(filepath=filepath)

    def loadMoveSet(self, filepath: str):
        self.roadmap = []
        if filepath[-3:] == "csv":
            df = pd.read_csv(filepath)
            # with open(filepath,"r") as roadmapFile:
                # spamreader = csv.reader(roadmapFile, delimiter=',')
                # spamreader = list(spamreader)

                # plats = list(spamreader)[:1][0]
                # self.roadmap = list(spamreader)[1:]
                # print(self.roadmap)

                # platines={ self.axis[i]:plats[i] for i in range(len(self.axis))}
        
                # self.saveSettings(platines=platines)
        elif filepath[-4:] == "xlsx":
            df = pd.read_excel(filepath)
            
        # print("DFFFF",list(df.columns))
        plats = list(df.values[:1][0])
        self.roadmap = [ list(pos) for pos in df.values[1:] ]
        # print(self.roadmap)
        logger.info("roadmap loaded")
        logger.debug(self.roadmap)

        platines={ self.axis[i]:plats[i] for i in range(len(self.axis))}

        # print(platines)
        logger.debug(f"platines loaded\n{platines}")

        self.saveSettings(platines=platines)

    def run(self, measurementFunc, speeds: list, *args, **kwargs):
        """
        Run a measure after every move. measurementFunc will be called as measurementFunc(position,*args,**kwargs)
        Parameters :
        - measurementFunc : a callable function without it's parameters.
        - speeds (list) : list of speeds for each axis.
        - *args : as many parameters without name for the measurementFunc.
        - **kwargs : as many parameters with a name for the the measurementFunc.
        """
        if self.roadmap is None:
            raise AttributeError("!! ERROR !! no roadmap has been loaded, use .loadMoveSet(filepath) before running")
        if not callable(measurementFunc):
            raise TypeError("!! ERROR !! measurementFunc must be callable !")

        self.move_finished_event = Event()
        
        aSpeeds = { self.axis[i]:speeds[i] for i in range(len(self.axis)) }
        for place in self.roadmap:
            aVals = { self.axis[i]:float(place[i]) for i in range(len(self.axis)) }

            # print("position:",aVals)
            # print("speeds:",aSpeeds)
            logger.debug(f"position : {aVals}")
            logger.debug(f"speeds : {aSpeeds}")
            self.move_finished_event.clear()
            cmd = self.mControl.absMove(aVals,aSpeeds,[self.move_finished_event.set])
            # print(f"command executed: {cmd}")
            logger.debug(f"move at {aVals}")
            while not self.move_finished_event.isSet():
                sleep(0.5)
            # print("start measurement")
            logger.debug("execute callback")
            measurementFunc(place,*args,**kwargs)

        logger.info("MoveAndMeasure run ended")

    def saveSettings(self, platines: dict = None, controller: str = None, port: str = None):
        if platines != None:
            plChoosed = {}
            for oneAxis in self.axis:
                # Platines to change
                if oneAxis in platines.keys() and "default" not in platines[oneAxis]:
                    plChoosed.update({
                        oneAxis: 
                        platines[oneAxis]
                    })
                # Platines to not touch
                else:
                    plChoosed.update({
                        oneAxis: 
                        self.mSettings.getSettingsDict()['parameters'][f'platine{oneAxis}']['default']
                    })
            platines = plChoosed
        
        self.mSettings.saveSettings(path, port=port, platines=platines, controller=controller)
        self.mSettings.loadSettings(path)
        self.settingsData = self.mSettings.getSettingsDict()

        return "0"

    def quit(self):
        self.mControl.quit()