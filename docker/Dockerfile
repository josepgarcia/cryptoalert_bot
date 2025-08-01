FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Dar permisos de ejecución al script principal
RUN chmod +x main.py

# Comando para ejecutar el bot
CMD ["python", "main.py"]