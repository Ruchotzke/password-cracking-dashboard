import json

import httpx
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.message import Message
from textual.widgets import Placeholder, Log, Button, Digits

class ControlPanel(Container):

    class PasswordsUpdatedMessage(Message):
        """
        A message used to share passwords upward.
        """

        def __init__(self, passwords):
            self.passwords = passwords
            super().__init__()

    def __init__(self, log: Log, *children):
        super().__init__(*children)

        self.id = "control-panel"
        self.logger = log

        self.url = f"http://127.0.0.1:5000/"

        self.password_queue_count = Digits("0000", id="web-server-count")
        self.password_queue_count.border_title = "Current Password Queue (WWW)"
        self.load_passwords = Button(label="Load Passwords", id="btn-load-passwords")

    def on_mount(self):
        self.set_interval(1, self.update_pulse)

    def compose(self) -> ComposeResult:
        """
        Lay out the controls container.
        :return:
        """
        with Vertical():
            with Horizontal(id="web-server-container"):
                self.password_queue_count.update("12345678")
                yield self.password_queue_count
                yield self.load_passwords

            yield Placeholder(id="Controls")

    async def update_pulse(self):
        """
        A pulse called to update WWW counts.
        :return:
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url + "curr_count")
            data = json.loads(response.content)
            self.password_queue_count.update(str(data["curr_count"]))


    async def on_button_pressed(self, event: Button.Pressed):
        """
        Callback for button press.
        :param event:
        :return:
        """
        self.logger.write_line("Requesting passwords...")
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url + "gather")
            data = json.loads(response.content)
            self.logger.write_line(f"t: {type(data)}, d: {data}")
            self.post_message(self.PasswordsUpdatedMessage(data["passwords"]))