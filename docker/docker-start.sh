#!/bin/bash

# Script para iniciar el bot de Telegram con Docker

echo "Iniciando el bot de Telegram con Docker..."

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "Error: Docker no está instalado. Por favor, instálalo antes de continuar."
    exit 1
fi

# Verificar si docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose no está instalado. Por favor, instálalo antes de continuar."
    exit 1
fi

# Verificar si el archivo config/config.env existe
if [ ! -f "config/config.env" ]; then
    echo "El archivo config/config.env no existe. Creando a partir del ejemplo..."
    if [ -f "config/config.env.example" ]; then
        cp config/config.env.example config/config.env
        echo "Se ha creado config/config.env a partir del ejemplo. Por favor, edita este archivo con tus propios valores antes de continuar."
        exit 1
    else
        echo "Error: No se encuentra el archivo config/config.env.example. No se puede continuar."
        exit 1
    fi
fi

# Construir y ejecutar el contenedor
echo "Construyendo y ejecutando el contenedor Docker..."
docker-compose up --build -d

echo ""
echo "El bot de Telegram se está ejecutando en un contenedor Docker."
echo "Para ver los logs, ejecuta: docker-compose logs -f"
echo "Para detener el bot, ejecuta: docker-compose down"