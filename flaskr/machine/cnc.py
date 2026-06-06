import linuxcnc

"""
Stateful design here: we should keep ONE connection open, not create
new ones. In other words, call connect once on startup.
"""

class Machine:
    def __init__(self):
        # Initialize any data structures and information *prior* to connecting to the machine.
        self.command_channel = None
        self.stat = None
        self.status = {}
        self.error_channel = None

        self.is_connected: bool = False
        self._is_ready: bool = False
        self._state: dict = {}

    def connect(self, use_error: bool = True) -> None:
        # Establish a persistent connection to the machine.
        self.command_channel = linuxcnc.command()
        self.stat = linuxcnc.stat()
        if use_error:
            self.error_channel = linuxcnc.error()

    def disconnect(self) -> None:
        # Disconnect from the machine.
        self.command_channel = None
        self.stat = None
        self.error_channel = None

    def is_ready(self) -> bool:
        # Return whether the machine is ready to receive commands.
        s = self.stat
        s.poll()

        return (not s.estop and s.enabled and (s.homed.count(1) == s.joints) and
                (s.interp_state == linuxcnc.INTERP_IDLE))

    def state(self) -> dict:
        # Poll the machine and return the LinuxCNC state dictionary.
        self.stat.poll()

        return {
            "is_estop": bool(self.stat.estop),
            "task_state": generate_task_state(self.stat)
        }

    # def estop(self) -> bool:
    #     # Send an emergency stop signal to the machine and return whether this succeeded.
    #     ...

def generate_task_state(state):
    if state.estop:
        return "STOPPED"
    else:
        match state.interp_state:
            case linuxcnc.INTERP_IDLE:
                return "READY"
            case linuxcnc.INTERP_READING:
                return "RUNNING"
            case linuxcnc.INTERP_PAUSED:
                return "PAUSED"
            case linuxcnc.INTERP_WAITING:
                return "DONE"
            case _:
                return "UNKNOWN"


"""
Do we want to define our own @dataclass for the state dictionary?
Might be more user-friendly (but also might not be worth it).
"""
