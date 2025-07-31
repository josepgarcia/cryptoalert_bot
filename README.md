# Bot de Alertas de Telegram

Este bot de Telegram está diseñado para responder a comandos básicos y ejecutar tareas programadas.

## Características

- Responde al comando `/ping` con "pong"
- Responde al comando `/status` con información del sistema
- Ejecuta una tarea programada cada X minutos (configurable)

## Requisitos

- Python 3.7 o superior
- Las dependencias listadas en `requirements.txt`

## Configuración

1. Asegúrate de tener un token de bot de Telegram. Si no tienes uno, puedes crear un bot a través de [@BotFather](https://t.me/BotFather) en Telegram.

2. Crea un archivo `config.env` basado en el archivo de ejemplo `config.env.example`:

```bash
cp config.env.example config.env
```

3. Edita el archivo `config.env` y configura tus propias variables de entorno:

```
# Configuración del Bot de Telegram
TELEGRAM_BOT_TOKEN=tu_token_aquí
TELEGRAM_CHAT_ID=tu_chat_id_aquí

# Configuración opcional
TELEGRAM_PARSE_MODE=HTML
TELEGRAM_DISABLE_WEB_PAGE_PREVIEW=false
TELEGRAM_DISABLE_NOTIFICATION=false

# Configuración del Bot
CRYPTO_CHECK_INTERVAL=5  # Intervalo en minutos para la tarea programada
```

## Instalación

1. Clona este repositorio:

```bash
git clone git@github.com:josepgarcia/cryptoalert_bot.git
cd cryptoalert_bot
```

2. Crea y activa un entorno virtual (recomendado):

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

Para iniciar el bot, puedes usar cualquiera de estos métodos:

### Método 1: Usando el script de inicio

```bash
./start.sh
```

Este script configurará automáticamente un entorno virtual, instalará las dependencias y ejecutará el bot.

### Método 2: Ejecución manual

```bash
python bot.py
```

### Comandos disponibles

- `/ping` - El bot responde con "pong"
- `/status` - El bot devuelve información del sistema donde se ejecuta

## Personalización

Puedes modificar el archivo `bot.py` para añadir más comandos o cambiar la funcionalidad de la tarea programada según tus necesidades.

## Licencia

Este proyecto está bajo la Licencia MIT.