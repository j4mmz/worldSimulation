#!/bin/bash
echo "Comprobando entorno virtual..."
if [ ! -d ".venv" ]; then
    echo "Creando entorno e instalando librerias con uv..."
    uv venv
    uv pip install -r requirements.txt
fi
echo "Lanzando Simulador..."
uv run python -m gui.app
