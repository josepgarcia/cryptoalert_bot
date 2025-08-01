# Bot de Alertas de Telegram

Este bot de Telegram está diseñado para responder a comandos básicos y ejecutar tareas programadas.
Hecho con IA y Python utilizando el IDE TRAE y 

## Características

- Responde al comando `/ping` con "pong"
- Responde al comando `/status` con información del sistema
- Ejecuta una tarea programada cada X minutos (configurable)

## Requisitos

### Para instalación local
- Python 3.7 o superior
- Las dependencias listadas en `requirements.txt`

### Para instalación con Docker
- Docker
- docker-compose

## Estructura del Proyecto

```
.
├── config/             # Archivos de configuración
│   └── config.env.example
├── data/               # Datos persistentes (base de datos)
├── docker/             # Archivos relacionados con Docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-start.sh
├── scripts/            # Scripts de utilidad
│   ├── init_git.sh
│   └── start.sh
├── src/                # Código fuente
│   ├── core/           # Componentes principales
│   │   ├── database.py
│   │   └── telegram_bot.py
│   ├── handlers/       # Manejadores de comandos
│   │   └── commands.py
│   └── bot.py          # Configuración principal del bot
└── main.py             # Punto de entrada principal
```

# Configuración

1. Asegúrate de tener un token de bot de Telegram. Si no tienes uno, puedes crear un bot a través de [@BotFather](https://t.me/BotFather) en Telegram.

2. Crea un archivo `config/config.env` basado en el archivo de ejemplo `config/config.env.example`:

```bash
cp config/config.env.example config/config.env
```

3. Edita el archivo `config/config.env` y configura tus propias variables de entorno:

```
# Configuración del Bot de Telegram
TELEGRAM_BOT_TOKEN=tu_token_aquí
TELEGRAM_CHAT_ID=tu_chat_id_aquí

# Configuración opcional
TELEGRAM_PARSE_MODE=HTML
TELEGRAM_DISABLE_WEB_PAGE_PREVIEW=false
TELEGRAM_DISABLE_NOTIFICATION=false

# Configuración del Bot
CRYPTO_CHECK_INTERVAL=60  # Intervalo en minutos para la tarea programada
CRYPTO_NOTIFICATION_COOLDOWN=3600  # Tiempo mínimo entre notificaciones (segundos)
CRYPTO_MAX_ALERTS_PER_TOKEN=5  # Máximo de alertas por token
CRYPTO_DEFAULT_PRICE_SOURCE=coingecko  # Fuente de precios por defecto
```
## Instalación

1. Clona este repositorio:

```bash
git clone git@github.com:josepgarcia/cryptoalert_bot.git
cd cryptoalert_bot
```

### Opción A: Instalación local

1. Crea y activa un entorno virtual (recomendado):

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

### Opción B: Instalación con Docker

1. Asegúrate de tener Docker y docker-compose instalados en tu sistema.

2. No es necesario instalar dependencias manualmente, ya que Docker se encargará de ello durante la construcción de la imagen.


## Uso

Para iniciar el bot, puedes usar cualquiera de estos métodos:

### Método 1: Usando el script de inicio

```bash
./scripts/start.sh
```

Este script configurará automáticamente un entorno virtual, instalará las dependencias y ejecutará el bot.

### Método 2: Ejecución manual

```bash
python main.py
```

### Método 3: Usando Docker

```bash
./scripts/docker-start.sh
```

Este script verificará que Docker y docker-compose estén instalados, comprobará la existencia del archivo `config/config.env`, y luego construirá y ejecutará el contenedor Docker.

Alternativamente, puedes ejecutar los comandos de Docker manualmente:

```bash
# Construir la imagen
docker-compose build

# Ejecutar el contenedor en segundo plano
docker-compose up -d

# Ver los logs
docker-compose logs -f

# Detener el contenedor
docker-compose down
```

### Comandos disponibles

- `/ping` - El bot responde con "pong"
- `/status` - El bot devuelve información del sistema donde se ejecuta

Estos comandos están disponibles en el teclado de Telegram para facilitar su uso. Aparecerán automáticamente en la interfaz del chat con el bot.

## Personalización

Puedes modificar el archivo `bot.py` para añadir más comandos o cambiar la funcionalidad de la tarea programada según tus necesidades.

## Licencia

Este proyecto está bajo la Licencia MIT.