"""
Stateful design here: we should keep ONE connection open, not create
new ones. In other words, call connect once on startup.
"""

class Machine:
    def __init__(self):
        # Initialize any data structures and information *prior* to connecting to the machine.
        self.command_channel = None
        self.stat_channel = None
        self.error_channel = None

        self.is_connected: bool = False
        ...

    def connect(self) -> bool:
        # Establish a persistent connection to the machine and return whether this was successful.
        ...

    def disconnect(self) -> bool:
        # Disconnect from the machine and return whether this was successful.
        ...

    def is_ready(self) -> bool:
        # Return whether the machine is ready to receive commands.
        ...

    def state(self) -> dict:
        # Poll the machine and return the LinuxCNC state dictionary.
        ...

    def estop(self) -> bool:
        # Send an emergency stop signal to the machine and return whether this succeeded.
        ...


"""
Do we want to define our own @dataclass for the state dictionary?
Might be more user-friendly (but also might not be worth it).
"""