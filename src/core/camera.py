import cv2
from threading import Thread
import time

class CameraStream: 
    """
    Clase para la lecturs de video de manera asíncrona
    Patrón: Producer-Consumer 
    El hilo 'update' produce frames y el hilo principal los consume.
    """
    
    def __init__(self, src=0, name = "CameraStream"): 
        """
        src: 0 para webcam, o ruta a un video
        """
        self.stream = cv2.VideoCapture(src) 

        if not self.stream.isOpened():
            raise ValueError(f"No se pudo abrir la cámara o video en la ruta {src}.")
        
        (self.grabbed, self.frame) = self.stream.read()
        
        # variable de control para el hilo
        self.name = name
        self.stopped = False

        # Métricas de rendimiento
        self.fps_start_time = None
        self.fps_frame_count = 0

    def start(self):
        """
        Inicia el hilo en segundo plano para actualizar los frames de video.
        """
        t = Thread(target=self.update,name = self.name,args=(), daemon=True) 
        t.start()
        self.fps_start_time = time.time() # Iniciar el temporizador de FPS
        return self

    def update(self):
        """
        Bucle que se ejecuta en el hilo para leer frames del video de manera continua.
        """
        while True: 
            if self.stopped: 
                return
            
            # Leer el siguiente frame del video
            (grabbed, frame) = self.stream.read() 
            
            if not grabbed: 
                self.stop()
                return
            
            self.frame = frame
            self.fps_frame_count += 1 
            
    def read(self): 
        """ Devuelve el frame más reciente leído por el hilo. """ 
        return self.frame 
    
    def stop(self):
         """ Detiene el hilo y libera los recursos de la cámara. """ 
         self.stopped = True 
            
    def get_fps(self):
        """ Calcula y devuelve los FPS actuales. """ 
        current_time = time.time() 
        elapsed = current_time - self.fps_start_time
        if elapsed > 0:
            return self.fps_frame_count / elapsed
        return 0.0 

    def release(self):
        """ Libera los recursos de la cámara. """ 
        self.stop()
        time.sleep(0.1) # Esperar un momento para asegurarse de que el hilo se detenga
        self.stream.release()

# Bloque de prueba
 
if __name__ == "__main__": 
    print("Iniciando setram asíncrono...")
    cam = CameraStream(src=0).start()
    time.sleep(1.0)

    print("Mostrando video. Presiona 'q' para salir.")
    while True:
        frame = cam.read() 
        if frame is not None: 
            cv2.imshow("CameraStream", frame) 
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break 
        else: 
            print("No se pudo leer el frame.") 

    print(f"FPS promedio: {cam.get_fps():.2f}")
    cam.release() 
    cv2.destroyAllWindows()
