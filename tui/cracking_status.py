from textual.app import ComposeResult
from textual.widgets import Placeholder, Sparkline, Label, Log
from textual.containers import Container, Horizontal

from hashcat.hashcat_runner import HashcatRunner


class StatusPane(Container):
    """
    A status pane for non-password-specific items.
    """
    def __init__(self, log: Log, *children):
        super().__init__(*children)

        self.id = "status-panel"

        self.logger = log

        self.overall_status = Label(id="overall-status", classes="status-text")
        self.overall_status.border_title = "Brute Force Status"

        # GPU Over time
        self.gpu_data = [0] * 100
        self.gpu_data[10] = 100
        self.gpu_data[20] = 30
        self.gpu_data[21] = 100
        self.gpu_data[55] = 25
        self.gpu_index = 0  # Current offset in graph

        self.gpu_graph = Sparkline(
            data=self.gpu_data,
            summary_function=max,
            id="GPU",)
        self.gpu_graph.border_title = "GPU Utilization"
        self.gpu_util = Label(id="GPU-util", classes="status-text")
        self.gpu_util.border_title = "GPU Util."
        self.gpu_temp = Label(id="GPU-temp", classes="status-text")
        self.gpu_temp.border_title = "GPU Temp."
        self.gpu_fan = Label(id="GPU-fan", classes="status-text")
        self.gpu_fan.border_title = "GPU Fan"
        self.gpu_mem = Label(id="GPU-mem", classes="status-text")
        self.gpu_mem.border_title = "GPU Mem."
        self.gpu_speed = Label(id="GPU-speed", classes="status-text")
        self.gpu_speed.border_title = "GPU Clock"

        self.start_time = Label(id="status-start-time", classes="status-text")
        self.start_time.border_title = "Brute Force Start"
        self.end_time = Label(id="status-estimated-end", classes="status-text")
        self.end_time.border_title = "Estimated End"

        self.hash_mode = Label(id="status-hash-mode", classes="status-text")
        self.hash_mode.border_title = "Hash Mode"
        self.queue = Label(id="status-queue", classes="status-text")
        self.queue.border_title = "Remaining Masks"
        self.crack_speed = Label(id="status-speed", classes="status-text")
        self.crack_speed.border_title = "Hash Speed"

        self.curr_mask = Label(id="status-mask", classes="status-text")
        self.curr_mask.border_title = "Current Mask"
        self.curr_prog = Label(id="status-progress", classes="status-text")
        self.curr_prog.border_title = "Guess Progress"

        self.guesses = Label(id="status-guesses", classes="status-text")
        self.guesses.border_title = "Current Guesses"

        self.progress = Label(id="status-progress", classes="status-text")
        self.progress.border_title = "Cracked Hashes"



    def compose(self) -> ComposeResult:
        """
        Lay out the status container.
        :return:
        """

        # Overall Status
        yield self.overall_status

        # GPU Utilization
        yield self.gpu_graph

        # GPU status
        with Horizontal(id="GPU-stats", classes="status-container"):
            yield self.gpu_util
            yield self.gpu_temp
            yield self.gpu_fan
            yield self.gpu_mem
            yield self.gpu_speed

        # Start/end time
        with Horizontal(id="status-times", classes="status-container"):
            yield self.start_time
            yield self.end_time

        # Cracking Metainfo
        with Horizontal(id="status-meta", classes="status-container"):
            yield self.hash_mode
            yield self.queue
            yield self.crack_speed

        # Current Mask
        with Horizontal(id="status-mask", classes="status-container"):
            yield self.curr_mask
            yield self.curr_prog

        # Current guess range
        yield self.guesses

        # Progress
        yield self.progress

    def update_gpu_data(self, new_sample: int) -> None:
        """
        Append this sample to the GPU data.
        Roll over if needed.
        :param new_sample:
        :return:
        """
        self.gpu_data[self.gpu_index] = new_sample
        self.gpu_index = (self.gpu_index + 1) % len(self.gpu_data)
        self.gpu_data[self.gpu_index] = 0   # To demarcate the update point

        self.gpu_graph.data = list(self.gpu_data)

    def update_content(self, runner: HashcatRunner) -> None:
        """
        Update the status based on current hash status.
        :param runner:
        :return:
        """
        if runner.is_running:
            self.overall_status.content = "RUNNING"
            # Update GPU
            util = runner.hardware[3].strip().strip().split()[0]
            self.gpu_util.content = util
            self.update_gpu_data(int(util.split("%")[0]))
            self.logger.write_line(str(int(util.split("%")[0])))
            # self.gpu_graph.data = self.gpu_data
            self.gpu_temp.content = runner.hardware[1].strip().split()[0]
            self.gpu_fan.content = runner.hardware[2].strip().strip().split()[0]
            self.gpu_mem.content = runner.hardware[5].strip().strip().split()[0]
            self.gpu_speed.content = runner.hardware[4].strip().strip().split()[0]

            # Update times
            self.start_time.content = ':'.join(runner.start_time)
            self.end_time.content = ':'.join(runner.estimated_time)

            # Metadata
            self.hash_mode.content = runner.hash_mode.strip()
            self.queue.content = runner.guess_queue.strip()
            self.crack_speed.content = runner.speed.strip()

            # Masking
            self.curr_mask.content = runner.mask[:runner.mask.index('[')].strip()
            self.curr_prog.content = runner.progress.strip()

            # Current Guesses
            self.guesses.content = ':'.join(runner.candidates)

            # Cracked Progress
            self.progress.content = runner.recovered.strip()
        else:
            self.overall_status.content = "OFFLINE"
            self.gpu_util.content = "0%"
            self.gpu_temp.content = "50c"
            self.gpu_fan.content = "0%"
            self.gpu_mem.content = "0Hz"
            self.gpu_speed.content = "0Hz"
            self.start_time.content = ""
            self.end_time.content = ""
            self.hash_mode.content = ""
            self.queue.content = ""
            self.crack_speed.content = "0 H/s"
            self.curr_mask.content = ""
            self.curr_prog.content = ""
            self.guesses.content = ""