from abc import ABC,abstractmethod

# Abstract class with all methods each language should implement. Functionalities of the app.
class Commands(ABC):
    """
    Summary:
        Abstract class definining mandatory methods each command language need to have implemented.
        Currently stopCmd and moveCmd are the mandatory methods.
    """
    def __init__(self, axis_speeds: dict = None):
        self.speeds = axis_speeds
    
    @abstractmethod
    def stopCmd(self)-> list:
        """
        Returns a list of commands to make a stop.
        """
        pass

    @abstractmethod
    def moveCmd(self, axis_values: dict)-> list:
        """
        Returns a list of commands to make a move.
        """
        pass

    @abstractmethod
    def goHome(self, nbAxis: int)-> list:
        """
        Returns a list of commands to go home
        """
        pass

    @abstractmethod
    def setHome(self, nbAxis: int)-> list:
        """
        Returns a list of commands to set current position as home
        """
        pass

    @abstractmethod
    def commandsToString(self, commands: list)-> list:
        """
        Returns a list of commands in string type
        """
        pass

class CSeries(Commands):
    """
    Summary:
        Commands language C-series extended from Commands abstract class. 
    """
    def __init__(self, axis_speeds: dict = None):
        super().__init__(axis_speeds)

    def stopCmd(self)-> str:
        """
        Returns one command to make the controller stop it's current action.
        """
        return list(["@0d\n\r".encode(encoding="ascii")])
    
    def moveCmd(self, axis_values: dict, axis_speeds: dict = None)-> list:
        """
        Parameters:
        - axis_values : dictionary of positions by axis to move to. Move to the specified position from it's current position. Unit is in steps.
        - axis_speeds : dictionary of speed values by axis. Speed set for each axis for the move to come. Unit is in step/s.
        Returns a list of two commands:
        - first one is to define axis that are concerned by the move.
        - second one is the movement command to specified position from current position.
        """
        commands = []
        # Define axis concerned
        commands.append(self.axisDefinitionCmd(len(axis_values)))
        # update movement speeds if redefined.
        if axis_speeds:
            self.speeds = axis_speeds
        # Create movement command
        axisStr = ""
        for axis,dist in axis_values.items():
            axisStr+=f"{int(round(dist))},{int(round(self.speeds[axis]))}," 
        commands.append(f"@0A {axisStr[:-1]}\n\r".encode("ascii"))

        return commands

    def goHome(self, nbAxis: int)-> list:
        return [f"@0R{self.axisDefinition(nbAxis=nbAxis)}".encode("ascii")]

    def setHome(self, nbAxis: int)-> list:
        return [f"@0n{self.axisDefinition(nbAxis=nbAxis)}".encode("ascii")]

    def commandsToString(self, commands: list)-> list:
        cmds = [cmd.decode("utf-8")[:-2] for cmd in commands]
        return "\n".join(cmds)

    def axisDefinitionCmd(self, nbAxis: int)-> str:
        """
        Parameters:
        - nbAxis : number of axis meant to move.
        Returns:
        - command to define axis meant to move.
        """
        axisDefCode = self.axisDefinition(nbAxis=nbAxis)
        return f"@0{axisDefCode}\n\r".encode("ascii")

    def axisDefinition(self, nbAxis: int)-> int:
        axisDefCode = 0
        if nbAxis == 1:
            axisDefCode = 1
        elif nbAxis == 2:
            axisDefCode = 3
        elif nbAxis == 3:
            axisDefCode = 7
        return axisDefCode

if __name__ == "__main__":
    print("start")
    cs = CSeries({'X':500, 'Y':300, 'Z':100})

    print(cs.moveCmd({'X': 300, 'Y':200, 'Z':100}))