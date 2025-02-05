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

class CSeries(Commands):
    def __init__(self, axis_values: dict, axis_speeds: dict):
        super().__init__(axis_values, axis_speeds)

    def stopCmd(self):
        return "@0R3\n\r".encode(encoding="ascii")
    
    def moveCmd(self):
        # maybe add axis definition command in return
        axisStr = ""
        for axis,dist in self.values.items():
            axisStr+=f"{dist},{self.speeds[axis]}," 
        return f"@0a {axisStr[:-1]}\n\r".encode("ascii")