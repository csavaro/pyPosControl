from serial import Serial
import serial.tools.list_ports
import time
import sys
import glob
import logging

logger = logging.getLogger(__name__)

class MissingValue(Exception):
    """
    Meant to be raise when a value like a setting is not set.
    """
    pass

class SerialConnection(Serial):
    """
    Manage a serial connection to send commands.
    
    Attributes:
        - port: str, port name of the connection.
        - baudrate: int, information signal speed, unit is baud/s.
        - timeout: int, maximum time to send a command without any response, unit is s.
        - bytesize: message length
        - parity 
    """
    def __init__(self, timeout: int = 10, bytesize: int = 8):
        """
        :param timeout: max waiting time when reading before aborting
        :type timeout: float | int
        :param bytesize: bytesize of the serial connection
        :type bytesize: int
        """
        super().__init__()
        self.port = None
        self.baudrate = 0
        self.timeout = timeout
        self.bytesize = bytesize
        self.parity = serial.PARITY_NONE

    def available_serial_ports(self):
        """
        Read the available serial ports names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :return: A list of the serial ports available on the system
        :rtype: list[str]
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

    def executeSelfCmd(self, commands, port=None):
        """
        Execute a single command or a list of commands.
        Open the serial link if necessary but let it open afterwards.
        
        Return options :
        - 0 if no acknowledge is recieved, all commands might not have been sent.
        - 1 if all commands were sent and all acknowledge revieved.

        :param commands: commands to be executed, byte format should be ascii.
        :type commands: str | byte | list[str|byte]
        :param port: *(Optional)* port to send commands to.
        :type port: str
        :return: success state of the transmission.
        :rtype: int
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

        # # Simulation
        # # TO_REMOVE OR COMMENT
        # logger.info("simulate connection...")
        # logger.debug(f"port: {port}")
        # logger.debug(f"baudrate: {self.baudrate}")
        # if isinstance(commands,(str,bytes)):
        #     commands = [commands]
        # for cmd in commands:
        #     logger.debug(f"launch cmd: {cmd}")
        #     time.sleep(1)
        # logger.info("...end of simulated connection")
        # return 1

        if not self.is_open:
            # print("Openning the serial connection")
            logger.info("Openning the serial connection")
            self.open()

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
                # print("launch cmd: ",cmd)
                logger.debug(f"launch cmd: {cmd}")
                self.write(cmd)
                # ack = self.readline()
                ack = self.read()
                try:
                    # print(f"recieved ({len(ack)}): {str(ack,'UTF-8')}")
                    logger.debug(f"raw recieved ({len(ack)}): {ack}")
                    logger.debug(f"recieved ({len(ack)}): {ack.decode('utf-16')}")
                except UnicodeDecodeError as e:
                    # print(f"WARNING : Could'nt decode a byte recieved after sending a command\n{e}")
                    logger.warning(f"WARNING : Could'nt decode a byte recieved after sending a command\n{e}")
                # check if an acknowledge is recieved
                if len(ack) == 0:
                    # print("no acknowledge recieved")
                    logger.debug("no acknowledge recieved")
                    # return 0
        # end of command transmission
        # print("end of command transmission")
        logger.debug("end of command transmission")
        return 1

    def executeCmd(self, commands, port=None):
        """
        Execute a single command or a list of commands.
        Open a serial link and close it afterwards.
        
        Return options :
        - 0 if no acknowledge is recieved, all commands might not have been sent.
        - 1 if all commands were sent and all acknowledge revieved.

        :param commands: commands to be executed, byte format should be ascii.
        :type commands: str | byte | list[str|byte]
        :param port: *(Optional)* port to send commands to.
        :type port: str
        :return: success state of the transmission.
        :rtype: int
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

        # # Simulation
        # # TO_REMOVE OR COMMENT
        # logger.info("simulate connection...")
        # logger.debug(f"port: {port}")
        # logger.debug(f"baudrate: {self.baudrate}")
        # if isinstance(commands,(str,bytes)):
        #     commands = [commands]
        # for cmd in commands:
        #     logger.debug(f"launch cmd: {cmd}")
        #     time.sleep(1)
        # logger.info("...end of simulated connection")
        # return 1

        # Execution
        with self as ser:
            ser.port        = port
            ser.baudrate    = self.baudrate
            ser.timeout     = self.timeout
            ser.bytesize    = self.bytesize
            ser.parity      = self.parity
            ser.open()
            # print("serial opened")
            logger.debug("serial opened")
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
                    # print("launch cmd: ",cmd)
                    logger.debug(f"launch cmd: {cmd}")
                    ser.write(cmd)
                    ack = ser.read()
                    try:
                        # print(f"recieved ({len(ack)}): {str(ack,'UTF-8')}")
                        logger.debug(f"recieved ({len(ack)}): {str(ack,'UTF-8')}")
                    except UnicodeDecodeError as e:
                        # print(f"WARNING : Could'nt decode a byte recieved after sending a command\n{e}")
                        logger.warning(f"WARNING : Could'nt decode a byte recieved after sending a command\n{e}")
                    # check if an acknowledge is recieved
                    if len(ack) == 0:
                        # print("no acknowledge recieved")
                        logger.debug("no acknowledge recieved")
                        # return 0
            # end of command transmission
            ser.close()
            # print("serial closed")
            logger.debug("serial closed")
        return 1

    def close(self):
        """
        Close the current serial link if it is open.
        """
        if self.is_open:
            # print("Closing the serial")
            logger.debug("Closing the serial")
            super().close()
        else:
            # print("serial is not open, already closed")
            logger.debug("serial is not open, already closed")