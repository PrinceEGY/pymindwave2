from enum import Enum


class ConnectionStatus(Enum):
    CONNECTED = 1
    DISCONNECTED = 2
    IDLE = 3
    SCANNING = 4
    NOTSCANNING = 5
    UNKOWN = 6
