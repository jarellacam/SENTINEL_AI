import sys
import os
import time
import cv2
import numpy as np
import yaml
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.camera import CameraStream
from src.core.storage import EvidenceSaver
from src.analysis.detector import Detector
from src.utils.notifier import NotificationManager
from src.core.database import DatabaseManager
from src.utils.alarm import AlarmManager

def load_config(path):
    with open(path, 'r') as f: return yaml.safe_load(f)

def is_inside_roi(box, roi_polygon):
    if not roi_polygon or len(roi_polygon) < 3: return False
    poly = np.array(roi_polygon, dtype=np.float32).reshape((-1, 1, 2))
    
    # CAMBIO CLAVE: Ahora probamos con el CENTRO del recuadro, no los pies
    center_x = float((box[0] + box[2]) / 2)
    center_y = float((box[1] + box[3]) / 2)
    return cv2.pointPolygonTest(poly, (center_x, center_y), False) >= 0

def main():
    load_dotenv()
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = load_config(os.path.join(ROOT_DIR, "config", "settings.yaml"))
    
    # Zona inicial por defecto si el archivo está corrupto
    DEFAULT_ROI = [[100, 350], [540, 350], [600, 480], [40, 480]]
    CURRENT_ROI = config['roi'].get('points', DEFAULT_ROI)
    
    db = DatabaseManager(os.path.join(ROOT_DIR, "sentinel_data.db"))
    notifier = NotificationManager(os.getenv("TG_TOKEN"), os.getenv("TG_CHAT_ID"), db_manager=db)
    detector = Detector(model_path=os.path.join(ROOT_DIR, "models", config['detector']['model_name']))
    alarm = AlarmManager(frequency=config['panic_mode']['frequency_hz'])
    saver = EvidenceSaver(folder=config['storage']['folder'], cooldown=config['storage']['cooldown'], notifier=notifier, db_manager=db)

    cam = CameraStream(src=0).start()
    cam.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(2.0)
    
    notifier.start_listening()
    notifier.send_text("🛡️ *Sentinel Pro activo*.")

    results = []
    f_count = 0
    intrusion_start_time = None
    panic_triggered = False

    try:
        while True:
            frame = cam.read()
            if frame is None: break
            frame = cv2.resize(frame, (640, 480))

            if notifier.capture_requested:
                path = os.path.join(ROOT_DIR, "captures", "manual.jpg")
                cv2.imwrite(path, frame)
                notifier.send_photo(path, "*Captura solicitada*.")
                notifier.capture_requested = False

            f_count += 1
            if f_count % 2 == 0:
                results = detector.predict(frame)

            intrusion = False
            display_frame = frame.copy()
            pts_draw = np.array(CURRENT_ROI, np.int32)
            cv2.polylines(display_frame, [pts_draw], True, (255, 165, 0), 2)

            for res in results:
                if res['class_name'] == "persona":
                    in_zone = is_inside_roi(res['box'], CURRENT_ROI)
                    color = (0, 0, 255) if in_zone else (255, 255, 255)
                    if in_zone: intrusion = True
                    
                    cv2.rectangle(display_frame, (res['box'][0], res['box'][1]), (res['box'][2], res['box'][3]), color, 2)
                    
                    # Marcador de diagnóstico en el CENTRO
                    cx, cy = int((res['box'][0] + res['box'][2])/2), int((res['box'][1] + res['box'][3])/2)
                    cv2.circle(display_frame, (cx, cy), 6, (255, 0, 0), -1)

            if intrusion:
                saver.save_intrusion(frame)
                if intrusion_start_time is None: intrusion_start_time = time.time()
                if (time.time() - intrusion_start_time) > config['panic_mode']['threshold_seconds']:
                    if not panic_triggered:
                        notifier.send_text(" *ALERTA DE MERODEO*")
                        alarm.start()
                        panic_triggered = True
            else:
                intrusion_start_time = None
                if panic_triggered:
                    alarm.stop(); panic_triggered = False

            cv2.imshow("Sentinel AI - Central Pro", display_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
    finally:
        alarm.stop(); cam.release(); cv2.destroyAllWindows()

if __name__ == "__main__":
    main()