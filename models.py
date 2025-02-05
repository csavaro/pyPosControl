class ModelSettings:
    def __init__(self, axis_names):
        self.port = None # from available ports
        self.stepscales = { axis_name:None for axis_name in axis_names } # platines
        self.baudrate = None # controller
    
    def getSettingsDict(self):
        pass

    def loadSettings(self, path):
        pass

class ModelControl:
    def __init__(self, axis_names):
        self.values = { axis_name:None for axis_name in axis_names } # usually in mm (unit)
        self.speeds = { axis_name:None for axis_name in axis_names } # usually in mm/s (unit/s)
    
    def setValue(self, axis, value):
        self.values.update({ axis:value })

    def setSpeed(self, axis, speed):
        self.speeds.update({ axis:speed })

if __name__ == "__main__":
    print("start models")