import time

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

    def wait(self) -> bool:
        # Return whether the wait-complete passed or raise an exception otherwise.
        match self.command_channel.wait_complete():
            case -1:
                raise MachineTimedOutError
            case linuxcnc.RCS_ERROR:
                raise MachineCommandError
            case linuxcnc.RCS_DONE:
                return True
            case _:
                raise MachineGeneralError

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

    def is_ready(self) -> tuple[bool, str]:
        # Return whether the machine is ready to receive commands.
        s = self.stat
        s.poll()

        def is_ready_str() -> str:
            # Return whether the machine is ready to receive commands as a string
            return (f"estop: not {bool(s.estop)}, enabled: {s.enabled}, all homed: {s.homed.count(1) == s.joints}, "
                    f"idle: {s.interp_state == linuxcnc.INTERP_IDLE}")

        return (not s.estop and s.enabled and (s.homed.count(1) == s.joints) and
                (s.interp_state == linuxcnc.INTERP_IDLE)), is_ready_str()


    def get_error(self) -> dict | None:
        # Return a formatted error or None if there is no error on the error channel.
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
        keys = ["is_estop", "task_state", "error", "position", "file"]
        self.stat.poll()

        state: dict = dict.fromkeys(keys, "")
        state["is_estop"] = bool(self.stat.estop)
        state["task_state"] = generate_task_state(self.stat)
        state["error"] = self.get_error()
        state["position"] = get_position(self.stat)
        state["file"] = self.stat.file

        return state

    def enable(self) -> bool:
        # Enable (power on) the machine.
        self.command_channel.state(linuxcnc.STATE_ON)

        # Sleep waiting for a response
        time.sleep(0.2)
        self.stat.poll()
        return self.stat.task_state == linuxcnc.STATE_ON

    def estop(self) -> None:
        # Send an emergency stop signal to the machine.
        self.command_channel.state(linuxcnc.STATE_ESTOP)

    def estop_reset(self) -> None:
        # Send an emergency stop reset signal (emergency stop OFF) to the machine.
        self.command_channel.state(linuxcnc.STATE_ESTOP_RESET)

    def load_file(self, file_path: str) -> None:
        # Load an NGC (G-code) file into LinuxCNC.
        if self.is_ready()[0]:
            self.command_channel.mode(linuxcnc.MODE_AUTO)
            self.command_channel.wait_complete()
            self.command_channel.program_open(file_path)
        else:
            raise MachineNotReadyError

    def start_program(self) -> None:
        # Start a program (assuming that a file has been loaded).
        self.stat.poll()
        if self.stat.file != "":
            if self.is_ready()[0]:
                # self.command_channel.reset_interpreter()
                self.command_channel.mode(linuxcnc.MODE_AUTO)
                self.command_channel.wait_complete()
                print("About to start!")
                self.command_channel.auto(linuxcnc.AUTO_RUN, 0)
            else:
                raise MachineNotReadyError
        else:
            raise ProgramNotLoadedError

    def pause(self) -> None:
        # Pause the current running program
        self.command_channel.auto(linuxcnc.AUTO_PAUSE)

    def unpause(self) -> None:
        # Unpause the current running program
        self.command_channel.auto(linuxcnc.AUTO_RESUME)

    def stop(self) -> None:
        # Stop the current running program
        self.command_channel.abort()

    def home_all(self) -> None:
        # Home all axes/joints
        self.command_channel.teleop_enable(False)
        self.wait()
        for joint in range(0, 4):
            self.command_channel.home(joint)
            self.wait()


class ProgramNotLoadedError(Exception):
    ...

class MachineNotReadyError(Exception):
    ...

class MachineCommandError(Exception):
    ...

class MachineTimedOutError(Exception):
    ...

class MachineGeneralError(Exception):
    ...



def generate_task_state(state) -> str:
    if state.estop:
        return "STOPPED"
    else:
        match state.interp_state:
            case linuxcnc.INTERP_IDLE:
                return "READY"
            case linuxcnc.INTERP_READING:
                return "READING"
            case linuxcnc.INTERP_PAUSED:
                return "PAUSED"
            case linuxcnc.INTERP_WAITING:
                return "RUNNING"
            case _:
                return "UNKNOWN"


def get_position(stat) -> list[float]:
    return [round(p, 4) for p in stat.actual_position[:3]]


"""
Do we want to define our own @dataclass for the state dictionary?
Might be more user-friendly (but also might not be worth it).
"""
