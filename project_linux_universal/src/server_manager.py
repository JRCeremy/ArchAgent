import os
import subprocess
import time


class ServerManager:
    def __init__(self):
        self.process = None
        self.current_model = None

    def start(self, model_path, context=1536, threads=6):
        self.stop()

        abs_model_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", model_path)
        )

        self.process = subprocess.Popen(
            [
                "llama-server",
                "-m", abs_model_path,
                "-c", str(context),
                "-t", str(threads),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        self.current_model = model_path
        time.sleep(2)

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            self.current_model = None
