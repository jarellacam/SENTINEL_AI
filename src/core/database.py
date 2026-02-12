import sqlite3
import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="sentinel_data.db"):
        self.db_path = os.path.abspath(db_path)
        self._initialize_db()

    def _initialize_db(self):
        """Crea la tabla y asegura que el esquema sea correcto (Auto-migración)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS events 
                           (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp DATETIME,
                            event_type TEXT,
                            image_path TEXT)''')
            
            # Verificación de integridad de columnas (Migración activa)
            cursor = conn.execute("PRAGMA table_info(events)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if "hash" not in columns:
                conn.execute("ALTER TABLE events ADD COLUMN hash TEXT DEFAULT 'no-hash'")
                conn.commit()

    def log_event(self, event_type, image_path, file_hash):
        """Registra una intrusión con su firma digital."""
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.datetime.now()
            conn.execute("INSERT INTO events (timestamp, event_type, image_path, hash) VALUES (?, ?, ?, ?)",
                         (now, event_type, image_path, file_hash))

    def verify_integrity(self):
        """Auditoría forense: verifica que los archivos no hayan sido alterados."""
        import hashlib
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT image_path, hash FROM events")
            rows = cursor.fetchall()
            errors = 0
            for path, reg_hash in rows:
                if not os.path.exists(path):
                    errors += 1
                    continue
                sha = hashlib.sha256()
                with open(path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""): sha.update(chunk)
                if sha.hexdigest() != reg_hash:
                    errors += 1
            return (errors == 0, errors)

    def get_last_24h_summary(self):
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT COUNT(*) FROM events WHERE timestamp > datetime('now', '-1 day')"
            return conn.execute(query).fetchone()[0]

    def get_last_event_details(self):
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT image_path, timestamp, hash FROM events ORDER BY timestamp DESC LIMIT 1"
            
            return conn.execute(query).fetchone()
    def clear_history(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM events")
            print("[DB] Historial limpiado para coherencia de integridad.")