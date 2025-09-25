from textual.app import App
from textual.widgets import Header, Footer

from tui.controls import ControlPanel
from tui.cracking_status import StatusPane
from tui.password_status import PasswordStatusBlock, PasswordStatusContainer


class PasswordDashboardApp(App):
    """ The app used to run the password dashboard."""

    CSS_PATH = "main.css"
    BINDINGS = [("d", "toggle_cracked", "Toggle dark mode")]

    passwords = ["1", "2", "3", "4", "5", "6", "7", "8"]
    password_container = PasswordStatusContainer([])
    cracked = False

    def action_toggle_cracked(self):
        self.cracked = not self.cracked
        for v in self.password_container.password_dict.values():
            v.finish_cracking()

    def on_mount(self) -> None:
        self.theme = "gruvbox"

    def compose(self):
        yield Header()

        # Status
        yield StatusPane(id="status-panel")

        # Controls
        yield ControlPanel(id="control-panel")

        # Passwords
        self.password_container = PasswordStatusContainer(self.passwords)
        yield self.password_container

        yield Footer()

    def action_toggle_dark(self):
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = PasswordDashboardApp()
    app.run()