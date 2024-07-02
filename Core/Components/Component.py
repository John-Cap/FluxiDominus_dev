
#Class component, base class for all components (including 'compound' components like a reactor?)

from Core.Control.Commands import Commands
from Core.Network.IP import IP


class ComponentBase:
    def __init__(self) -> None:
        self.ip = IP() #TODO-> class IP()
        self.commands = Commands()
        self.status = {} #latest returned 
        pass

    def sendCommand(command): #Params ["_command"]
        pass

class Component(ComponentBase):
    def __init__(self) -> None:
        super().__init__()