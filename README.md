# Sentinel AI 

Sentinel AI es un sistema de videovigilancia inteligente de última milla (Edge AI) que combina detección de objetos en tiempo real, integridad de evidencias mediante criptografía y notificaciones interactivas vía Telegram.

Desarrollado con un enfoque en **Privacidad Total** y **Seguridad Forense**, el sistema procesa todo localmente sin depender de nubes externas.

## Características Principales

* **IA :** Detección de personas mediante YOLOv8 optimizado con ONNX Runtime.
* **Integridad de Evidencias:** Cada captura se firma con un hash **SHA-256** único, almacenado en una base de datos SQLite para garantizar que las pruebas no han sido manipuladas.
* **Modo Pánico :** Alarma sonora disuasoria integrada que se activa si un sujeto permanece en la zona de vigilancia más tiempo del permitido.
* **Gestión de ROI Visual:** Interfaz gráfica para dibujar polígonos de vigilancia personalizados con el ratón.
* **Control Dual:** Panel de control local (Tkinter) y control remoto total mediante un Bot de Telegram interactivo.

##  Stack Tecnológico

* **Lenguaje:** Python 3.11+
* **Visión Artificial:** OpenCV / YOLOv8 (ONNX)
* **Base de Datos:** SQLite3
* **Comunicaciones:** Telegram Bot API
* **Seguridad:** Hash SHA-256 (Hashlib)

## Instalación y Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/jarellacam/SENTINEL_AI.git](https://github.com/tu-usuario/sentinel_ai.git)
    cd sentinel_ai
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` en la raíz con tus credenciales:
    ```env
    TG_TOKEN=tu_token_de_telegram
    TG_CHAT_ID=tu_chat_id
    ```

4.  **Ejecutar:**
    Usa el lanzador incluido:
    ```batch
    iniciar_sentinel.bat
    ```

##  Comandos de Telegram

El bot permite interactuar con el sistema en tiempo real:
* `/report`: Genera un informe de actividad de las últimas 24h y verifica la integridad de todos los archivos.
* `/capture`: Solicita una fotografía en tiempo real de la cámara.
* `/mute [minutos]`: Silencia las notificaciones de intrusión durante el tiempo especificado.

## ⚖️ Aviso Legal
Este software es una herramienta de seguridad experimental. El usuario es responsable de cumplir con las leyes locales de videovigilancia y protección de datos (RGPD en la UE). Se recomienda no apuntar a la vía pública.

Juan Arellano Cameo
www.linkedin.com/in/juann-arellano

