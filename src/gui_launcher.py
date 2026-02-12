import tkinter as tk
from tkinter import messagebox, ttk
import yaml
import os
from dotenv import set_key, load_dotenv

class SentinelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sentinel AI - Panel de Control Pro")
        self.root.geometry("450x600")
        self.root.configure(padx=20, pady=20)
        
        # Cargar datos actuales
        load_dotenv()
        self.config_path = "config/settings.yaml"
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self._create_widgets()

    def _create_widgets(self):
        # Título
        tk.Label(self.root, text="SENTINEL AI CONFIG", font=("Arial", 16, "bold")).pack(pady=10)

        # Sección Telegram
        group_tg = tk.LabelFrame(self.root, text=" Comunicaciones (Telegram) ", padx=10, pady=10)
        group_tg.pack(fill="x", pady=5)

        tk.Label(group_tg, text="Bot Token:").pack(anchor="w")
        self.ent_token = tk.Entry(group_tg, show="*")
        self.ent_token.insert(0, os.getenv("TG_TOKEN") or "")
        self.ent_token.pack(fill="x", pady=2)

        tk.Label(group_tg, text="Chat ID:").pack(anchor="w")
        self.ent_chat = tk.Entry(group_tg)
        self.ent_chat.insert(0, os.getenv("TG_CHAT_ID") or "")
        self.ent_chat.pack(fill="x", pady=2)

        # Sección Alarma
        group_alarm = tk.LabelFrame(self.root, text=" Modo Pánico (Merodeo) ", padx=10, pady=10)
        group_alarm.pack(fill="x", pady=5)

        tk.Label(group_alarm, text="Segundos para activar:").pack(anchor="w")
        self.spn_time = tk.Spinbox(group_alarm, from_=1, to=60)
        self.spn_time.delete(0, "end")
        self.spn_time.insert(0, self.config['panic_mode']['threshold_seconds'])
        self.spn_time.pack(fill="x", pady=2)

        tk.Label(group_alarm, text="Frecuencia Sonido (Hz):").pack(anchor="w")
        self.spn_freq = tk.Spinbox(group_alarm, from_=400, to=5000, increment=100)
        self.spn_freq.delete(0, "end")
        self.spn_freq.insert(0, self.config['panic_mode']['frequency_hz'])
        self.spn_freq.pack(fill="x", pady=2)

        # Botón Guardar y Lanzar
        tk.Button(self.root, text="DIBUJAR ZONA DE VIGILANCIA", command=self.open_roi_selector, 
          bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(fill="x", pady=5)
        
        tk.Button(self.root, text="GUARDAR CONFIGURACIÓN", command=self.save, 
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), height=2).pack(fill="x", pady=20)
        
        tk.Button(self.root, text="INICIAR VIGILANCIA", command=self.launch, 
                  bg="#2196F3", fg="white", font=("Arial", 10, "bold"), height=2).pack(fill="x")

    def save(self):
        try:
            # Guardar en .env
            set_key(".env", "TG_TOKEN", self.ent_token.get())
            set_key(".env", "TG_CHAT_ID", self.ent_chat.get())
            
            # Guardar en YAML
            self.config['panic_mode']['threshold_seconds'] = int(self.spn_time.get())
            self.config['panic_mode']['frequency_hz'] = int(self.spn_freq.get())
            
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f)
            
            messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def launch(self):
        self.save()
        messagebox.showinfo("Sentinel", "El sistema se iniciará. Cierra esta ventana si deseas detener el panel.")
        os.system("python src/main.py")
    
    def open_roi_selector(self):
        os.system("python src/utils/roi_selector.py")
        # Recargar config por si cambió la ROI
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

if __name__ == "__main__":
    root = tk.Tk()
    app = SentinelGUI(root)
    root.mainloop()

d