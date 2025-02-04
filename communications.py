from abc import ABC,abstractmethod

# Abstract class with all methods each language should implement. Functionalities of the app.
class Commands(ABC):
    def __init__(self, axis_values: dict, axis_speeds: dict = None):
        self.values = axis_values
        self.speeds = axis_speeds
    
    @abstractmethod
    def stopCmd(self):
        pass

    @abstractmethod
    def moveCmd(self):
        pass

