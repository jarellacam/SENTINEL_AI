@echo off
:: Configuración de ventana
title Sentinel AI Pro - Centro de Control
color 0b
cls

echo ===================================================
echo           S E N T I N E L   A I   P R O
echo           Sistemas de Vigilancia Inteligente
echo ===================================================
echo.
echo [SISTEMA] Iniciando entorno de ejecucion...

:: 1. Activar el entorno de Anaconda
:: Intentamos la ruta estandar, si falla avisamos al usuario.
if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\anaconda3\Scripts\activate.bat"
) else (
    echo [ERROR] No se encontro Anaconda en la ruta estandar.
    echo Intentando ejecucion directa...
)

:: 2. Lanzar la interfaz grafica
echo [SISTEMA] Abriendo Panel de Control...
python src/gui_launcher.py

:: 3. Manejo de errores tras cerrar la interfaz
if %errorlevel% neq 0 (
    echo.
    echo ---------------------------------------------------
    echo [ERROR] El programa se cerro con errores. 
    echo Verifique que las librerias esten instaladas:
    echo pip install -r requirements.txt
    echo ---------------------------------------------------
    pause
)

echo.
echo [INFO] Sentinel AI Pro se ha cerrado correctamente.
echo Presione cualquier tecla para salir.
pause > nul