#!/bin/bash

# Script para iniciar el bot de Telegram

echo "Iniciando el bot de Telegram..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado. Por favor, instálalo antes de continuar."
    exit 1
fi

# Verificar si el entorno virtual existe, si no, crearlo
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
    echo "Entorno virtual creado."
fi

# Activar el entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Verificar si el archivo config.env existe
if [ ! -f "config.env" ]; then
    echo "Error: El archivo config.env no existe. Por favor, crea este archivo con la configuración necesaria."
    exit 1
fi

# Dar permisos de ejecución al script del bot
chmod +x bot.py

# Iniciar el bot
echo "Iniciando el bot..."
python3 bot.py