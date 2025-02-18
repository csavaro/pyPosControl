from abc import ABC,abstractmethod

# Abstract class with all methods each language should implement. Functionalities of the app.
class Commands(ABC):
    def __init__(self, axis_speeds: dict = None):
        self.speeds = axis_speeds
    
    @abstractmethod
    def stopCmd(self)-> list:
        pass

    @abstractmethod
    def moveCmd(self, axis_values: dict)-> list:
        pass

class CSeries(Commands):
    def __init__(self, axis_speeds: dict = None):
        super().__init__(axis_speeds)

    def stopCmd(self)-> str:
        return "@0d\n\r".encode(encoding="ascii")
    
    def moveCmd(self, axis_values: dict, axis_speeds: dict = None)-> list:
        commands = []
        commands.append(self.axisDefinitionCmd(len(axis_values)))
        # maybe add axis definition command in return
        if axis_speeds:
            self.speeds = axis_speeds
        axisStr = ""
        for axis,dist in axis_values.items():
            axisStr+=f"{int(round(dist))},{int(round(self.speeds[axis]))}," 
        commands.append(f"@0a {axisStr[:-1]}\n\r".encode("ascii"))
        return commands
    
    def axisDefinitionCmd(self, nbAxis: int):
        axisDefCode = 0
        if nbAxis == 1:
            axisDefCode = 1
        elif nbAxis == 2:
            axisDefCode = 3
        elif nbAxis == 3:
            axisDefCode = 7
        return f"@0{axisDefCode}".encode("ascii")

if __name__ == "__main__":
    print("start")
    cs = CSeries({'X':500, 'Y':300, 'Z':100})

    print(cs.moveCmd({'X': 300, 'Y':200, 'Z':100}))