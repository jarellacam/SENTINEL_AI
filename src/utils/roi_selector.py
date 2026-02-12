import cv2
import yaml
import numpy as np
import os

class ROISelector:
    def __init__(self, config_path="config/settings.yaml"):
        # Localizar la ruta absoluta para evitar errores de carpeta
        self.config_path = os.path.abspath(config_path)
        self.points = []
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            print(f"[ERROR] No se encuentra el archivo: {self.config_path}")

    def _mouse_callback(self, event, x, y, flags, param):
        # Esta es la parte que registra los clics
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append([x, y])
            print(f"[CLICK] Punto registrado en: {x}, {y}")

    def run(self):
        print("[SISTEMA] Iniciando selector... Espera a que abra la ventana.")
        cap = cv2.VideoCapture(0)
        
        # Forzamos resolución para evitar descuadres
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Capturamos varios frames para que la cámara se ajuste a la luz
        for _ in range(10): cap.read()
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("[ERROR] No se pudo obtener imagen de la cámara.")
            return

        # Aseguramos que el frame sea exactamente 640x480
        frame = cv2.resize(frame, (640, 480))

        # Nombre de ventana constante para evitar errores de callback
        win_name = "CONFIGURAR ZONA"
        cv2.namedWindow(win_name)
        cv2.setMouseCallback(win_name, self._mouse_callback)

        print("\n--- INSTRUCCIONES ---")
        print("1. Haz CLIC IZQUIERDO para poner los puntos.")
        print("2. Presiona 'S' para GUARDAR y cerrar.")
        print("3. Presiona 'C' para LIMPIAR los puntos.")
        print("4. Presiona 'Q' para SALIR sin guardar.")

        while True:
            display = frame.copy()
            
            # Dibujar los puntos y las líneas mientras el usuario hace clic
            if len(self.points) > 0:
                for p in self.points:
                    cv2.circle(display, (p[0], p[1]), 5, (0, 255, 0), -1)
                
                if len(self.points) > 1:
                    pts_arr = np.array(self.points, np.int32)
                    cv2.polylines(display, [pts_arr], True, (255, 165, 0), 2)

            cv2.imshow(win_name, display)
            
            # Traer la ventana al frente
            cv2.setWindowProperty(win_name, cv2.WND_PROP_TOPMOST, 1)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s') and len(self.points) >= 3:
                self._save_config()
                break
            elif key == ord('c'):
                print("[SISTEMA] Puntos limpiados.")
                self.points = []
            elif key == ord('q'):
                print("[SISTEMA] Saliendo sin guardar.")
                break

        cv2.destroyAllWindows()

    def _save_config(self):
        self.config['roi']['points'] = self.points
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f)
        print(f"✅ Zona guardada correctamente con {len(self.points)} puntos.")

if __name__ == "__main__":
    selector = ROISelector()
    selector.run()