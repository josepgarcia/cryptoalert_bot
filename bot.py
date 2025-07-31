#!/usr/bin/env python3
import os
import time
import platform
import psutil
import logging
import threading
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde config.env
load_dotenv('config.env')

# Configuración del bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CRYPTO_CHECK_INTERVAL = int(os.getenv('CRYPTO_CHECK_INTERVAL', '5'))

# Comandos del bot
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde con 'pong' cuando recibe el comando /ping"""
    await update.message.reply_text('pong')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Devuelve información del sistema donde se ejecuta el bot"""
    system_info = {
        'Sistema Operativo': platform.system() + ' ' + platform.release(),
        'Versión de Python': platform.python_version(),
        'CPU': platform.processor(),
        'Uso de CPU': f"{psutil.cpu_percent()}%",
        'Memoria RAM': f"{psutil.virtual_memory().percent}% usado",
        'Tiempo de ejecución': str(datetime.now()),
        'Hostname': platform.node()
    }
    
    message = "📊 <b>Información del Sistema</b>\n\n"
    for key, value in system_info.items():
        message += f"<b>{key}:</b> {value}\n"
    
    await update.message.reply_text(message, parse_mode='HTML')

# Función para la tarea programada
async def scheduled_task(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje programado al chat"""
    await context.bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text="🔔 Ejecución programada",
        parse_mode='HTML'
    )

def main() -> None:
    """Inicia el bot y configura los manejadores de comandos"""
    # Crear la aplicación y pasarle el token del bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Registrar los manejadores de comandos
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("status", status_command))

    # Configurar la tarea programada (cada X minutos)
    job_queue = application.job_queue
    job_queue.run_repeating(scheduled_task, interval=CRYPTO_CHECK_INTERVAL * 60, first=10)

    # Iniciar el bot
    logger.info("Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling()

if __name__ == '__main__':
    main()