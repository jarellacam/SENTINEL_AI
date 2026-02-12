import requests
import threading
import time
import datetime
import os

class NotificationManager:
    def __init__(self, token, chat_id, db_manager=None):
        self.token = token
        self.chat_id = chat_id
        self.db = db_manager
        self.api_url = f"https://api.telegram.org/bot{self.token}/"
        self.last_update_id = 0
        self.mute_until = None
        self.capture_requested = False

    def is_muted(self):
        return self.mute_until and datetime.datetime.now() < self.mute_until

    def send_text(self, message):
        payload = {'chat_id': self.chat_id, 'text': message, 'parse_mode': 'Markdown'}
        threading.Thread(target=lambda: requests.post(self.api_url + "sendMessage", data=payload), daemon=True).start()

    def send_photo(self, photo_path, caption):
        if self.is_muted(): return
        def _task():
            try:
                time.sleep(0.5)
                with open(photo_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {'chat_id': self.chat_id, 'caption': caption, 'parse_mode': 'Markdown'}
                    requests.post(self.api_url + "sendPhoto", files=files, data=data, timeout=10)
            except Exception as e: print(f"[ERR NOTIFIER] {e}")
        threading.Thread(target=_task, daemon=True).start()

    def start_listening(self):
        threading.Thread(target=self._poll_messages, daemon=True).start()

    def _poll_messages(self):
        while True:
            try:
                url = f"{self.api_url}getUpdates?offset={self.last_update_id + 1}&timeout=10"
                resp = requests.get(url, timeout=15).json()
                if "result" in resp:
                    for update in resp["result"]:
                        self.last_update_id = update["update_id"]
                        if "message" in update and "text" in update["message"]:
                            text = update["message"]["text"]
                            if text == "/report": self._handle_report()
                            elif text == "/capture": self.capture_requested = True
                            elif text.startswith("/mute"): self._handle_mute(text)
                time.sleep(1)
            except Exception: pass

    def _handle_mute(self, text):
        try:
            mins = int(text.split()[1]) if len(text.split()) > 1 else 60
            self.mute_until = datetime.datetime.now() + datetime.timedelta(minutes=mins)
            self.send_text(f"*Sentinel silenciado* por {mins} minutos.")
        except: self.send_text("Uso: `/mute [minutos]`")

    def _handle_report(self):
        if not self.db: return
        is_ok, errs = self.db.verify_integrity()
        count = self.db.get_last_24h_summary()
        status = "Integridad: `OK`" if is_ok else f" Integridad: `{errs} FALLOS`"
        msg = f"*REPORTE SENTINEL*\nIntrusiones (24h): `{count}`\n{status}"
        last = self.db.get_last_event_details()
        if last and os.path.exists(last[0]): self.send_photo(last[0], msg)
        else: self.send_text(msg)