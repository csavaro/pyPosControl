class ModeleSettings:
    def __init__(self):
        self.unit = None
        self.port = None
        self.baudrate = None
        self.steprate = None

    def load(self, filepath):
        self.unit = None
        self.port = None
        self.baudrate = None
        self.steprate = None