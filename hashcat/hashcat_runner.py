import asyncio
import subprocess

from textual import work
from textual.widgets import Log

class HashcatRunner:
    """
    A class used to handle running hashcat async.
    """

    def __init__(self, log: Log, on_update):
        """
        Initialize the hashcat runner.
        """
        self.is_running = False     # Whether or not this process is actively running
        self.updated = False        # Flag which swaps to true when anything has been updated
        self.log = log              # A logger for any log writing updates
        self.process = None         # The process running hashcat
        self.worker = None          # The worker running the subprocess
        self.on_update = on_update  # The callback for updating the GUI as hashcat updates.

        # Status characteristics
        self.status = ""
        self.hash_mode = ""
        self.hash_target = ""
        self.start_time = ""
        self.estimated_time = ""
        self.kernel = ""
        self.mask = ""
        self.charset = ""
        self.guess_queue = ""
        self.speed = ""
        self.recovered = ""
        self.progress = ""
        self.rejected = ""
        self.restore_point = ""
        self.restore_sub = ""
        self.engine = ""
        self.candidates = ""
        self.hardware = ""
        self.cracked = []

        # Needed to avoid first update woes
        self.first_update = True


    def run(self, md5_path: str):
        """
        Start running the brute forcer.
        :param md5_path: The path to a file full of md5 hashes.
        :return:
        """
        if self.is_running:
            self.log.write_line("Unable to start a second concurrent hashcat session.")
            return
        self.first_update = True
        self.worker = asyncio.create_task(self._run_hashcat(md5_path))

    async def _run_hashcat(self, md5_path: str):
        """
        A textual worker to run hashcat's parsing in the background.
        Avoids blocking.
        :param md5_path:
        :return:
        """
        # Set up the process
        self.log.write_line("Starting hashcat in brute force mode.")
        self.is_running = True  # Set this at the start
        self.cracked = []

        try:
            self.process = await asyncio.create_subprocess_shell(
                cmd=f"hashcat -m0 {md5_path} -a3 -1 ?l?d!@#$% ?1?1?1?1?1?1?1?1?1?1 -i --quiet --status --status-timer 1 --potfile-disable",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Read the output for as long as the pipe is open
            while True:
                # Get the next line or exit
                line = await self.process.stdout.readline()
                if not line:
                    # The pipe has closed
                    break

                # Process the line
                line = line.decode("utf-8").strip()
                self.update_from_line(line)

            await self.process.wait()
            self.log.write_line(f"Hashcat exited ({self.process.returncode})")
        except asyncio.CancelledError:
            self.log.write_line("Hashcat task was cancelled")
            raise
        finally:
            self.is_running = False

    def update_from_line(self, line: str):
        """
        Update the current status from the provided line
        :param line:
        :return:
        """
        line = line.strip().split(":")
        if line[0].startswith("Session"):
            # If we hit this point, tell the GUI to update (as we've got a fresh update for it)
            if self.first_update:
                self.first_update = False
            else:
                self.on_update()
        elif line[0].startswith("Status"):
            # Status of this queued task
            self.status = line[1]
        elif line[0].startswith("Hash.Mode"):
            # Current hash mode
            self.hash_mode = line[1]
        elif line[0].startswith("Hash.Target"):
            # Targeted hash
            self.hash_target = line[1]
        elif line[0].startswith("Time.Started"):
            # Start time for this task
            self.start_time = line[1:]
        elif line[0].startswith("Time.Estimated"):
            # Estimated end time for this task
            self.estimated_time = line[1:]
        elif line[0].startswith("Kernel"):
            # Kernel Feature
            self.kernel = line[1]
        elif line[0].startswith("Guess.Mask"):
            # Current mask
            self.mask = line[1]
            # print(line[1])
        elif line[0].startswith("Guess.Charset"):
            # Current charsets
            self.charset = line[1]
        elif line[0].startswith("Guess.Queue"):
            # Current queued task
            self.guess_queue = line[1]
        elif line[0].startswith("Speed"):
            # Current hashing speed
            self.speed = line[1]
            self.speed = self.speed[:self.speed.index("(")].strip()
        elif line[0].startswith("Recovered"):
            # How many hashes have been recovered
            self.recovered = line[1]
        elif line[0].startswith("Progress"):
            # Current progress through this set of guesses
            self.progress = line[1]
        elif line[0].startswith("Rejected"):
            # No idea
            self.rejected = line[1]
        elif line[0].startswith("Restore.Point"):
            # Restore point
            self.restore_point = line[1]
        elif line[0].startswith("Restore.Sub"):
            # ???
            self.restore_sub = line[1:]
        elif line[0].startswith("Candidate.Engine"):
            # ???
            self.engine = line[1]
        elif line[0].startswith("Candidates"):
            # Current guess candidates for this status message
            self.candidates = line[1:]
        elif line[0].startswith("Hardware"):
            # Current hardware status
            self.hardware = line[1:]
        else:
            # Not part of the status, so this must be a hash!
            self.cracked.append(line)
            self.on_update()

    async def stop(self):
        """
        If running, stop hashcat.
        :return:
        """
        if self.process and self.process.returncode is None:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()

        if self.worker and not self.worker.done():
            self.worker.cancel()
            try:
                await self.worker
            except asyncio.CancelledError:
                pass

        self.is_running = False
        self.on_update()