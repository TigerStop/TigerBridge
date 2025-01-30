import socket
import threading
import select

from types import FunctionType
from enum import IntEnum, StrEnum

PORT = 7071

class TSPro:
    """
    The interface class for the TigerStop Pro
    """

    class EVENT_CODES(IntEnum):
        """
        An enum of integer codes to identify different types of messages.
        """
        MOVE_FINISHED     = 0
        RECEIVED_SETTING  = 1
        RECEIVED_POSITION = 2
        ERROR             = 3
        TOOL_ENGAGED      = 4
        TOOL_DISENGAGED   = 5

    class ERROR_CODES(IntEnum):
        """
        An enum of integer codes to identify different types of errors.
        """
        SUCCESS                      = 100
        BEYOND_MIN_LIMIT             = 101
        BEYOND_MAX_LIMIT             = 102
        UNEXPECTED_OBSTRUCTION       = 103
        UNEXPECTED_MOVEMENT          = 104
        INVALID_DESTINATION          = 105
        INVALID_COMMAND              = 106
        INVALID_SETTING              = 107
        MOVEMENT_BUSY                = 108
        UNDER_VOLTAGE                = 109
        OVER_VOLTAGE                 = 110
        OVER_TEMPERATURE             = 111
        OVER_TEMPERATURE_RATE        = 112
        OVER_CURRENT                 = 113
        STOPPED                      = 114
        MOVED_WHILE_TOOL_CYCLING     = 115
        TOOL_CYCLED_WHILE_MOVING     = 116
        INVALID_CALIBRATION_POSITION = 117

    class SETTING_NAMES(StrEnum):
        """
        An enum of setting names
        """

        MINIMUM_LIMIT = "minlim"
        MAXIMUM_LIMIT = "maxlim"

    class MESSAGE_REQUEST_PREFIXES(StrEnum):
        """
        An enum of strings to prefix to messages sent to the TigerStop.
        """
        MOVE_TO_POSITION = "move_to"
        GET_SETTING      = "get_setting"
        GET_POSITION     = "get_position"
        STOP             = "stop"
        CALIBRATE        = "calibrate"
        HOME             = "home"

    __delim_char           = "|"
    __movement_in_progress = False
    __read_buffer: list    = []
    __event_dict           = {}
    __event_dict_mutex     = threading.Lock()
    __socket: socket.socket
    __socket_read_thread: threading.Thread

    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setblocking(True)

    def __del__(self):
        if self.__socket != None:
            self.__socket.close()

    def __parse_line(self, line: str) -> list[str]:
        """
        Decode a bytearray and split it using the internal delimiter character

        @return list[str]
        """

        return line.split(self.__delim_char)

    def __format_message(self, *args: any) -> bytes:
        """
        Join all provided arguments into a string using the internal delimiter character and appended with a newline,
        then return this message encoded as a bytes object.

        @param args tuple[any]: data to include in the message
        @return bytes
        """

        # convert all arguments to strings,
        # then concatenate all those strings with "|" between each one,
        # and finally, append a newline.
        message = self.__delim_char.join(map(str, args)) + "\n"
        return message.encode()

    def __send_formatted_message(self, *args: any):
        """
        Send a message over the socket that has been formatted using __format_message.
        """

        message = self.__format_message(*args)
        print(f"sending message {message}")

        try:
            self.__socket.send(message)
        except socket.error:
            raise

    def __socket_read(self, connection: socket.socket):
        """
        The function body for this class's socket reading thread.
        """

        while True:
            line = self.__socket.makefile().readline()
            print(f"received message: {line}")
            segments = self.__parse_line(line)

            try:
                event_id = int(segments[0])
            except ValueError:
                continue

            # call the event hook for the received event_id
            if event_id in self.__event_dict and callable(self.__event_dict[event_id]):
                # *segments[1:] passes all message segments after the first as arguments to the event's callback function
                self.__event_dict_mutex.acquire()
                self.__event_dict[event_id](*segments[1:])
                self.__event_dict_mutex.release()

    def set_event_hook(self, event_id: int, callback: FunctionType):
        """
        Set a callback function to be called when the specified event_id is received over the socket connection.
        """

        # __event_dict is modified in the main thread, separate from when it is accessed in the socket read thread.
        # this mutex to makes sure this process is thread-safe
        self.__event_dict_mutex.acquire()
        self.__event_dict[event_id] = callback
        self.__event_dict_mutex.release()

    def remove_event_hook(self, event_id: int):
        """
        Remove the event callback for the specified event_id
        """

        # __event_dict is modified in the main thread, separate from when it is accessed in the socket read thread.
        # this mutex to makes sure this process is thread-safe
        self.__event_dict_mutex.acquire()
        del self.__event_dict[event_id]
        self.__event_dict_mutex.release()

    def request_move_to_position(self, position: float):
        """
        Signal the TigerStop to move to the provided position.
        The sent message string is formatted like so: "move_to|{position}\n",
        where {position} is a string-formatted floating point value
        """

        prefix = TSPro.MESSAGE_REQUEST_PREFIXES.MOVE_TO_POSITION
        position = str(position)
        self.__send_formatted_message(prefix, position)

    def request_stop(self):
        """
        Signal the TigerStop to stop movement.
        The sent message string is formatted like so: "stop\n"
        """

        prefix = TSPro.MESSAGE_REQUEST_PREFIXES.STOP
        self.__send_formatted_message(prefix)

    def request_current_position(self):
        """
        Ask the TigerStop for the current position.
        The home routine causes the machine finds an initial reference point to ensure accurate positioning.
        The sent message string is formatted like so: "get_position\n"
        """

        prefix = TSPro.MESSAGE_REQUEST_PREFIXES.GET_POSITION
        self.__send_formatted_message(prefix)

    def request_calibrate(self, position: float):
        """
        Signal the TigerStop to calibrate to the given position.
        The sent message string is formatted like so: "calibrate|{position}\n",
        where {position} is a string-formatted floating point value
        """

        prefix = TSPro.MESSAGE_REQUEST_PREFIXES.CALIBRATE
        self.__send_formatted_message(prefix, position)

    def request_home(self):
        """
        Signal the TigerStop to perform a home routine.
        The sent message string is formatted like so: "home\n",
        """

        prefix = TSPro.MESSAGE_REQUEST_PREFIXES.HOME
        self.__send_formatted_message(prefix)

    def connect(self, ip_address: str) -> bool:
        """
        Attempt to create a TCP socket connection to the provided ip ip_address

        @param ip_address str
        @return bool: True on successful connection, False otherwise
        """

        try:
            self.__socket.connect((ip_address, PORT))
            self.__socket_read_thread = threading.Thread(target = self.__socket_read, args = (self.__socket,))
            self.__socket_read_thread.start()
            return True
        except socket.error as error:
            print(error)
            return False
