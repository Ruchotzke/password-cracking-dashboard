import subprocess

from textual.app import App
from textual.widgets import Header, Footer, Log, Placeholder

from hashcat.dictionary_attack import try_dictionary_attack

from tui.controls import ControlPanel
from tui.cracking_status import StatusPane
from tui.password_status import PasswordStatusBlock, PasswordStatusContainer


class PasswordDashboardApp(App):
    """ The app used to run the password dashboard."""

    CSS_PATH = "main.css"
    BINDINGS = [("d", "try_dictionary", "Try dictionary attack"),
                ("e", "load_wordlist", "Load Wordlist")]

    passwords = ["1", "2", "3", "4", "5", "6", "7", "8"]
    password_container = PasswordStatusContainer([])
    cracked = False
    log_pane = Log(id="log")

    def action_toggle_cracked(self):
        self.cracked = not self.cracked
        for v in self.password_container.password_dict.values():
            v.finish_cracking()

    async def action_load_wordlist(self):
        """
        Load the wordlist for cracking
        :return:
        """
        # Hash the passwords (using the original file)
        self.log_pane.write_line("Hashing wordlist")
        with open("plain.txt", "r") as plaintext_handle, open("md5.txt", "w") as output_file:
            hasher_process = subprocess.Popen(
                ['python', 'hashcat/hasher.py'],
                stdin=plaintext_handle,
                stdout=output_file,
            )
            hasher_process.wait()

        # Load the passwords
        passwords = []
        self.log_pane.write_line("Loading passwords")
        with open("plain.txt", 'r') as plain, open("md5.txt", "r") as md5:
            plain_lines = plain.readlines()
            md5_lines = md5.readlines()
            for i in range(0, len(md5_lines)):
                passwords.append((plain_lines[i].strip(), md5_lines[i].strip()))

        # Clear out the old display
        await self.password_container.clear_passwords(self.log_pane)

        # Load all new passwords
        for (pw, md5) in passwords:
            await self.password_container.add_password(pw, md5)

    async def action_try_dictionary(self):
        """
        Attempt a dictionary attack
        :return:
        """
        result = try_dictionary_attack("md5.txt", self.log_pane)
        self.log_pane.write_line(f"Results: {result}")

    def on_mount(self) -> None:
        self.theme = "gruvbox"

    def compose(self):
        yield Header()

        # Log
        yield self.log_pane

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