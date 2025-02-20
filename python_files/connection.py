from serial import Serial
import serial.tools.list_ports
import time
import sys
import glob

class MissingValue(Exception):
    pass

class SerialConnection:
    def __init__(self, timeout: int = 10, bytesize: int = 8):
        self.port = None
        self.baudrate = None
        self.timeout = timeout
        self.bytesize = bytesize
        self.parity = serial.PARITY_NONE

    def available_serial_ports(self):
        """
        Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def executeCmd(self, commands, port=None):
        """
        Execute a single command or a list of commands.
        Params:
            - commands: str,byte,list of str or list of bytes - commands to be executed, byte format should be ascii.
            - port (Optional) : port to send to commands to.
        Returns: 
            - 0 if no acknowledge is recieved, all commands might not have been sent.
            - 1 if all commands were sent and all acknowledges recieved.
        """
        if not port:
            port = self.port
        if not port:
            raise MissingValue("Missing setting: port is not set. Either give it in function param or set it in class attribute")
        if not self.baudrate or self.baudrate <= 0:
            raise MissingValue("Missing setting: baudrate is not set. Set it in class attribute")
        if not self.bytesize or self.bytesize <= 0:
            raise MissingValue("Missing setting: bytesize is not set. Set it in class attribute")
        if not self.parity:
            raise MissingValue("Missing setting: parity is not set. Set it in class attribute")

        # Simulation
        # TO_REMOVE
        print("sim connection...")
        print("port: ",port)
        print("baudrate:",self.baudrate)
        if isinstance(commands,(str,bytes)):
            commands = [commands]
        for cmd in commands:
            print("launch cmd:",cmd)
            time.sleep(1)
        print("...end of sim connection")
        return 1

        # Execution
        with serial.Serial() as ser:
            ser.port        = port
            ser.baudrate    = self.baudrate
            ser.timeout     = self.timeout
            ser.bytesize    = self.bytesize
            ser.parity      = self.parity
            ser.open()
            print("serial opened")
            # Manage single command
            if(isinstance(commands,bytes) or isinstance(commands,str)):
                commands = [commands]
            # Execute commands
            for cmd in commands:
                # encode to ascii format if not already done
                if isinstance(cmd,str):
                    cmd = cmd.encode("ascii")
                # execute command if good format
                if isinstance(cmd,bytes):
                    print("sending ",cmd)
                    ser.write(cmd)
                    ack = ser.read()
                    try:
                        print(f"recieved ({len(ack)}): {str(ack,'UTF-8')}")
                    except UnicodeDecodeError as e:
                        print("WARNING : Could'nt decode a byte recieved after sending a command")
                        print(e)
                    # check if an acknowledge is recieved
                    if len(ack) == 0:
                        print("no acknowledge recieved")
                        return 0
            # end of command transmission
            ser.close()
        return 1

