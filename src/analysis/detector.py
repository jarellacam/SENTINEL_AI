import cv2
import numpy as np
import onnxruntime as ort

class Detector:
    """
    Clase para realizar detección de objetos utilizando un modelo ONNX. 
    """
    def __init__(self, model_path, conf_threshold=0.5): 
        self.conf_threshold = conf_threshold
        
        # Cargar el modelo ONNX
        print(f"cargando modelo ONNX desde {model_path}...")
        self.session = ort.InferenceSession(model_path ,providers=['CPUExecutionProvider']) 

        # Sacar los nombres de las entradas y salidas del modelo
        self.input_name = self.session.get_inputs()[0].name 
        self.input_shape = self.session.get_inputs()[0].shape

        self.img_size = 640

        # Classes for object detection
        self.classes = {0: 'persona', 1: 'bicicleta', 2: 'coche', 3: 'moto', 
                        4: 'avión', 5: 'autobús', 6: 'tren', 7: 'camión', 8: 'barco', 9: 'semáforo'}
        
    def preprocess(self, frame): 
        """ Preprocesa el frame para que sea compatible con el modelo ONNX. """ 
        # Redimensionar a 640x640 (lo que pide YOLO)
        self.original_height, self.original_width = frame.shape[:2]
        img = cv2.resize(frame, (self.img_size, self.img_size))
        
        # Convertir BGR a RGB y cambiar orden de ejes (H,W,C) -> (C,H,W)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.transpose((2, 0, 1)) 
        
        # Normalizar (0-255 -> 0.0-1.0) y añadir dimensión de batch
        img = np.expand_dims(img, axis=0)
        img = img.astype(np.float32) / 255.0
        return img
    
    def predict(self, frame):
        """
        Realiza la inferencia y devuelve las detecciones limpias.
        Retorna: Lista de diccionarios [{'class': 'persona', 'box': [x1, y1, x2, y2], 'conf': 0.85}, ...]
        """
        input_tensor = self.preprocess(frame)
        
        # Inferencia 
        outputs = self.session.run(None, {self.input_name: input_tensor})
        
        # Post-procesamiento (YOLOv8 ONNX devuelve una matriz compleja, hay que decodificarla)
        predictions = np.squeeze(outputs[0]).T
        
        results = []
        
        # Filtrado rápido 
        scores = np.max(predictions[:, 4:], axis=1)
        predictions = predictions[scores > self.conf_threshold, :]
        scores = scores[scores > self.conf_threshold]
        
        if len(predictions) == 0:
            return []

        # Obtener clases
        class_ids = np.argmax(predictions[:, 4:], axis=1)
        
        # Obtener cajas (xywh -> xyxy) y reescalar al tamaño original
        boxes = predictions[:, :4]
        
        # Escalar de 640x640 al tamaño real de la imagen
        x_factor = self.original_width / self.img_size
        y_factor = self.original_height / self.img_size

        input_boxes = boxes.copy()
        input_boxes[:, 0] = (boxes[:, 0] - boxes[:, 2] / 2) * x_factor
        input_boxes[:, 1] = (boxes[:, 1] - boxes[:, 3] / 2) * y_factor
        input_boxes[:, 2] = (boxes[:, 0] + boxes[:, 2] / 2) * x_factor
        input_boxes[:, 3] = (boxes[:, 1] + boxes[:, 3] / 2) * y_factor
        
        # Aplicar Non-Maximum Suppression (NMS) para quitar cajas duplicadas
        indices = cv2.dnn.NMSBoxes(input_boxes.tolist(), scores.tolist(), self.conf_threshold, 0.45)
        
        for i in indices:
            # cv2.dnn.NMSBoxes devuelve una lista de listas en algunas versiones, o lista plana en otras
            index = i if isinstance(i, (int, np.integer)) else i[0]
            
            box = input_boxes[index]
            results.append({
                "class_id": int(class_ids[index]),
                "class_name": self.classes.get(class_ids[index], "objeto"),
                "confidence": float(scores[index]),
                "box": box.astype(int).tolist() # [x1, y1, x2, y2]
            })
            
        return results
        
    