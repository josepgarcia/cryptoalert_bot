# Guía de Contribución

¡Gracias por tu interés en contribuir a este proyecto! Aquí hay algunas pautas para ayudarte a empezar.

## Configuración del Entorno de Desarrollo

1. Clona el repositorio:
   ```bash
   git clone git@github.com:josepgarcia/cryptoalert_bot.git
   cd cryptoalert_bot
   ```

2. Crea tu archivo de configuración a partir del ejemplo:
   ```bash
   cp config.env.example config.env
   ```
   Luego edita `config.env` con tus propios valores.

### Opción A: Entorno Local

1. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. Instala las dependencias de desarrollo:
   ```bash
   pip install -r requirements.txt
   ```

### Opción B: Usando Docker

1. Asegúrate de tener Docker y docker-compose instalados en tu sistema.

2. Construye y ejecuta el contenedor para desarrollo:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

3. Para ver los logs durante el desarrollo:
   ```bash
   docker-compose logs -f
   ```

4. Para detener el contenedor:
   ```bash
   docker-compose down
   ```

## Proceso de Contribución

1. Crea una nueva rama para tu característica o corrección:
   ```bash
   git checkout -b feature/nombre-de-tu-caracteristica
   ```
   o
   ```bash
   git checkout -b fix/nombre-de-tu-correccion
   ```

2. Realiza tus cambios y asegúrate de que el código funcione correctamente.

3. Haz commit de tus cambios:
   ```bash
   git add .
   git commit -m "Descripción clara de los cambios realizados"
   ```

4. Envía tus cambios a GitHub:
   ```bash
   git push origin nombre-de-tu-rama
   ```

5. Crea un Pull Request en GitHub.

## Estilo de Código

- Sigue las convenciones de estilo de PEP 8 para Python.
- Escribe docstrings para todas las funciones, clases y métodos.
- Mantén las líneas de código con un máximo de 88 caracteres.
- Usa nombres descriptivos para variables y funciones.

## Pruebas

Asegúrate de que tu código pase todas las pruebas existentes y, si es posible, añade nuevas pruebas para las características que implementes.

## Informar Problemas

Si encuentras un error o tienes una sugerencia para mejorar el proyecto, por favor crea un issue en GitHub con la siguiente información:

- Descripción clara del problema o sugerencia
- Pasos para reproducir el problema (si aplica)
- Comportamiento esperado vs. comportamiento actual
- Capturas de pantalla (si aplica)
- Entorno (sistema operativo, versión de Python, etc.)

## Preguntas

Si tienes alguna pregunta sobre cómo contribuir, no dudes en abrir un issue con tu pregunta.

¡Gracias por tu contribución!