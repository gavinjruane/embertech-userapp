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

    def connect(self) -> None:
        # Establish a persistent connection to the machine.
        self.command_channel = linuxcnc.command()
        self.stat = linuxcnc.stat()
        self.error_channel = linuxcnc.error_channel()

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

    def get_error(self) -> dict | None:
        e = self.error_channel.poll()
        if e:
            kind, text = e
            if kind in (linuxcnc.NML_ERROR, linuxcnc.OPERATOR_ERROR):
                return {
                    "error": text,
                    "type": "error"
                }
            else:
                return {
                    "error": text,
                    "type": "information"
                }

        return None

    def state(self) -> dict:
        # Poll the machine and return the LinuxCNC state dictionary.
        keys = ["is_estop", "task_state", "error", "position"]
        self.stat.poll()

        state: dict = dict.fromkeys(keys, "")
        state["is_estop"] = bool(self.stat.estop)
        state["task_state"] = generate_task_state(self.stat)
        state["error"] = self.get_error()
        state["position"] = get_position(self.stat)

        return state

    def estop(self) -> None:
        # Send an emergency stop signal to the machine.
        self.command_channel.state(linuxcnc.STATE_ESTOP)

    def estop_reset(self) -> None:
        # Send an emergency stop reset signal (emergency stop OFF) to the machine.
        self.command_channel.state(linuxcnc.STATE_ESTOP_RESET)


def generate_task_state(state) -> str:
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


def get_position(state) -> list[float]:
    position = []

    for i in range(state.joints):
        position.append(round(state.joint[i]["output"], 4))

    return position


"""
Do we want to define our own @dataclass for the state dictionary?
Might be more user-friendly (but also might not be worth it).
"""
