import threading
import time
import winsound

class AlarmManager:
    def __init__(self, frequency=1000, duration=500):
        self.frequency = frequency
        self.duration = duration
        self.is_ringing = False
        self._stop_event = threading.Event()

    def _ring_task(self):
        while not self._stop_event.is_set():
            # Hace sonar un "BIP" de Windows
            winsound.Beep(self.frequency, self.duration)
            time.sleep(0.1) # Pausa entre pitidos

    def start(self):
        if not self.is_ringing:
            self.is_ringing = True
            self._stop_event.clear()
            threading.Thread(target=self._ring_task, daemon=True).start()

    def stop(self):
        self._stop_event.set()
        self.is_ringing = False