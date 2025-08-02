#!/usr/bin/env python3
import os
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from src.handlers.commands import ping_command, status_command, send_report_command, alert_command, scheduled_task, scheduled_command, remove_command, tokenprice_command, post_init, init_telegram_bot

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde config.env
config_path = Path(__file__).parent.parent / 'config' / 'config.env'
load_dotenv(config_path)

# Configuración del bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Configuración de criptomonedas
CRYPTO_CHECK_INTERVAL = int(os.getenv('CRYPTO_CHECK_INTERVAL', '60'))
CRYPTO_NOTIFICATION_COOLDOWN = int(os.getenv('CRYPTO_NOTIFICATION_COOLDOWN', '3600'))
CRYPTO_MAX_ALERTS_PER_TOKEN = int(os.getenv('CRYPTO_MAX_ALERTS_PER_TOKEN', '5'))
CRYPTO_DEFAULT_PRICE_SOURCE = os.getenv('CRYPTO_DEFAULT_PRICE_SOURCE', 'coingecko')
CRYPTO_EXCHANGE = os.getenv('CRYPTO_EXCHANGE', 'binance')
CRYPTO_MAX_ALERTS_PER_USER = int(os.getenv('CRYPTO_MAX_ALERTS_PER_USER', '10'))
CRYPTO_CLEANUP_DAYS = int(os.getenv('CRYPTO_CLEANUP_DAYS', '7'))

# No hay comandos aquí, se han movido a commands.py
    
def main() -> None:
    """Inicia el bot y configura los manejadores de comandos"""
    # Inicializar la instancia de TelegramBot
    init_telegram_bot()
    logger.info("Instancia de TelegramBot inicializada")
    
    # Crear la aplicación y pasarle el token del bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    # Registrar los manejadores de comandos
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("report", send_report_command))
    application.add_handler(CommandHandler("alert", alert_command))
    application.add_handler(CommandHandler("scheduled", scheduled_command))
    application.add_handler(CommandHandler("remove", remove_command))
    application.add_handler(CommandHandler("tokenprice", tokenprice_command))

    # Configurar la tarea programada (cada X minutos)
    job_queue = application.job_queue
    job_queue.run_repeating(scheduled_task, interval=CRYPTO_CHECK_INTERVAL * 60, first=10)

    # Iniciar el bot
    logger.info("Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling()

if __name__ == '__main__':
    main()