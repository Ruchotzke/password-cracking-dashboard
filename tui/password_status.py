from datetime import timedelta
from math import floor
from time import monotonic

from textual.app import ComposeResult
from textual.containers import Horizontal, Container
from textual.reactive import reactive
from textual.renderables.digits import Digits
from textual.widget import Widget
from textual.widgets import Label


class PasswordStatusContainer(Container):
    """
    A container for all of the passwords being actively cracked.
    """

    def __init__(self, passwords: list, **kwargs):
        super().__init__(**kwargs)  # Pass any Container-specific kwargs up
        self.passwords = passwords
        self.password_dict = {}

    def compose(self) -> ComposeResult:
        """

        :param passwords: The passwords being cracked.
        :return:
        """
        self.id = "password-status-container"
        for password in self.passwords:
            # Yield a new child
            child = PasswordStatusBlock(password)
            self.password_dict[password] = child
            yield child



class PasswordStatusBlock(Container):
    """
    A container for a single password being cracked.
    """

    start_time = reactive(monotonic)
    curr_time = reactive(0.0)

    def __init__(self, password: str, **kwargs):
        super().__init__(**kwargs)  # Pass any Container-specific kwargs up
        self.time_label = Label("0m 00s 0000ms", id="password-time")
        self.password = password
        self.cracking = True

    def on_mount(self) -> None:
        self.set_interval(1.0/60, self.update_time)

    def update_time(self):
        if self.cracking:
            self.curr_time = monotonic() - self.start_time

    def watch_curr_time(self):
        td = timedelta(seconds=self.curr_time)
        mins = td.seconds // 60
        secs = td.seconds % 60
        millis = td.microseconds // 1000
        self.time_label.update(f"{mins}m {secs:02d}s {millis:03d}ms")

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.password, id="password-password")
            yield self.time_label

        self.add_class("password-status")
        self.add_class("cracking")

    def finish_cracking(self) -> None:
        if self.cracking:
            self.add_class("cracked")
            self.remove_class("cracking")
            self.cracking = False