@echo off
echo ============================================================
echo  Agente de Productores v2 - instalando y probando
echo ============================================================
echo.
echo Paso 1/3: instalando dependencias (puede tardar un minuto)...
pip install -r requirements.txt
echo.
echo Paso 2/3: prueba con datos inventados (no toca tu Firebase real)...
python smoke_test.py
echo.
echo Paso 3/3: abriendo el agente en tu navegador (http://127.0.0.1:5000)...
echo Para cerrarlo, volve a esta ventana negra y apreta Ctrl+C, o cerrala.
echo.
python run_web.py
pause
