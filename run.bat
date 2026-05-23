@echo off
echo Comprobando entorno virtual...
if not exist .venv (
    echo Creando entorno e instalando librerias con uv...
    uv venv
    uv pip install -r requirements.txt
)
echo Lanzando Simulador...

set PYTHONPATH=.

uv run python gui/app.py
pause