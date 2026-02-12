import os
import cv2
import time
import datetime
import threading
import hashlib

class EvidenceSaver:
    def __init__(self, folder="captures", cooldown=15, notifier=None, db_manager=None):
        self.folder = folder
        self.cooldown = cooldown
        self.notifier = notifier
        self.db = db_manager
        self.last_save = 0
        os.makedirs(self.folder, exist_ok=True)

    def save_intrusion(self, frame):
        """Inicia el protocolo de guardado si no estamos en tiempo de espera."""
        now = time.time()
        if now - self.last_save > self.cooldown:
            self.last_save = now
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(self.folder, f"INTRUSION_{ts}.jpg")
            # El guardado es asíncrono para no congelar la IA
            threading.Thread(target=self._do_save, args=(frame.copy(), path), daemon=True).start()

    def _do_save(self, frame, path):
        """Guarda la imagen, calcula su Hash SHA-256 y registra en DB."""
        cv2.imwrite(path, frame)
        
        # Generar firma digital de la evidencia
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""): sha.update(chunk)
        f_hash = sha.hexdigest()

        if self.db: 
            self.db.log_event("INTRUSION", path, f_hash)
        
        if self.notifier:
            self.notifier.send_photo(path, f"*INTRUSIÓN DETECTADA*\nIntegridad: `{f_hash[:10]}...`")