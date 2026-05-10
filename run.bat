@echo off
echo Comprobando entorno virtual...
if not exist .venv (
    echo Creando entorno e instalando librerias con uv...
    uv venv
    uv pip install -r requirements.txt
)
echo Lanzando Simulador...
uv run python -m gui.app
pause
