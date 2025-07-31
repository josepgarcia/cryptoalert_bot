#!/bin/bash

# Script para inicializar el repositorio de Git

echo "Inicializando repositorio Git para el bot de Telegram..."

# Verificar si Git está instalado
if ! command -v git &> /dev/null; then
    echo "Error: Git no está instalado. Por favor, instálalo antes de continuar."
    exit 1
fi

# Inicializar repositorio Git si no existe
if [ ! -d ".git" ]; then
    echo "Inicializando repositorio Git..."
    git init
    echo "Repositorio Git inicializado."
else
    echo "El repositorio Git ya está inicializado."
fi

# Añadir archivos al staging area
echo "Añadiendo archivos al staging area..."
git add .

# Verificar si hay archivos en el staging area
if git diff --staged --quiet; then
    echo "No hay cambios para hacer commit."
    exit 0
fi

# Hacer el primer commit
echo "Haciendo el primer commit..."
git commit -m "Commit inicial: Bot de Telegram para alertas"

echo ""
echo "Repositorio Git inicializado correctamente."
echo "Para añadir un repositorio remoto, ejecuta:"
echo "git remote add origin git@github.com:josepgarcia/cryptoalert_bot.git"
echo "git branch -M main"
echo "git push -u origin main"