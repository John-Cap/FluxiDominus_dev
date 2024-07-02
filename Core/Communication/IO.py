
import sys

class IOBase:
    def __init__(self) -> None:
        pass

class IO(IOBase):
    def __init__(self) -> None:
        super().__init__()

    def read(self):
        return (
            sys.
            stdin.
            readline().
            strip()
        )
    
    def write(self,output=""):
        if (isinstance(output,str)):
            print(output,flush=True)
        else:
            print(str(output),flush=True)
