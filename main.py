import asyncio
import subprocess

from textual.app import App
from textual.reactive import reactive
from textual.widgets import Header, Footer, Log, Placeholder

from hashcat.dictionary_attack import try_dictionary_attack
from hashcat.hashcat_runner import HashcatRunner

from tui.controls import ControlPanel
from tui.cracking_status import StatusPane
from tui.password_status import PasswordStatusBlock, PasswordStatusContainer


class PasswordDashboardApp(App):
    """ The app used to run the password dashboard."""

    CSS_PATH = "main.css"
    BINDINGS = [("d", "try_dictionary", "Try dictionary attack"),
                ("e", "load_wordlist", "Load Wordlist"),
                ("b", "run_bruteforce", "Run Brute Force attack"),
                ("k", "kill_bruteforce", "Kill brute force attack")]

    passwords = ["1", "2", "3", "4", "5", "6", "7", "8"]
    password_container = PasswordStatusContainer([])
    cracked = False
    log_pane = Log(id="log")
    hashcat_runner = None

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
        self.log_pane.write_line("Trying dictionary")
        result = await try_dictionary_attack("md5.txt", self.log_pane)
        self.log_pane.write_line(f"Results: {result}")
        for pwd in result:
            self.password_container.password_dict[pwd].finish_cracking()

    async def action_run_bruteforce(self) -> None:
        """
        Run a bruteforce attack against the passwords.
        :return:
        """
        self.hashcat_runner.run("md5.txt")

    async def action_kill_bruteforce(self) -> None:
        self.log_pane.write_line("Killing hashcat brute force.")
        await self.hashcat_runner.stop()

    def hashcat_updated(self) -> None:
        """
        A callback used to update the GUI as hashcat updates.
        :return:
        """
        for pwd in self.hashcat_runner.cracked:
            self.password_container.password_dict[pwd[1]].finish_cracking()

    def on_mount(self) -> None:
        self.theme = "gruvbox"
        self.hashcat_runner = HashcatRunner(self.log_pane, self.hashcat_updated)

    async def on_unmount(self) -> None:
        await self.hashcat_runner.stop()

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