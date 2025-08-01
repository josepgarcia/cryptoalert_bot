#!/usr/bin/env python3
import os
import platform
import psutil
import logging
from datetime import datetime
from telegram import Update, BotCommand
from telegram.ext import ContextTypes, Application
from src.core.telegram_bot import TelegramBot
from src.core.database import CryptoDatabase

# Configurar logging
logger = logging.getLogger(__name__)

# Variables globales para las instancias
telegram_bot = None
db = None

# Comandos del bot
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde con 'pong' cuando recibe el comando /ping"""
    # Mantenemos la respuesta directa para comandos interactivos
    await update.message.reply_text('pong')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Devuelve información del sistema donde se ejecuta el bot"""
    global telegram_bot
    if telegram_bot is None:
        telegram_bot = TelegramBot()
    
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
    
    # Para respuestas interactivas, seguimos usando el método de la API de python-telegram-bot
    # ya que necesitamos responder directamente al mensaje del usuario
    await update.message.reply_text(message, parse_mode='HTML')
    
    # También podemos usar nuestra clase TelegramBot para enviar mensajes adicionales si es necesario
    # telegram_bot.send_message("Mensaje adicional de estado")

# Función para enviar un informe detallado
async def send_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un informe detallado usando la clase TelegramBot"""
    global telegram_bot
    if telegram_bot is None:
        telegram_bot = TelegramBot()
    
    # Crear un mensaje con formato HTML más complejo
    report = f"""<b>📈 INFORME DETALLADO</b>

<i>Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>

<b>Estadísticas del Sistema:</b>
• CPU: {psutil.cpu_percent()}%
• RAM: {psutil.virtual_memory().percent}%
• Disco: {psutil.disk_usage('/').percent}%

<b>Información de Red:</b>
• Hostname: {platform.node()}
• Sistema: {platform.system()} {platform.release()}

<code>Este es un informe automático generado por el bot.</code>
"""
    
    # Enviar el informe usando la clase TelegramBot
    telegram_bot.send_message(report)
    
    # Informar al usuario que el informe ha sido enviado
    await update.message.reply_text("✅ Informe detallado enviado al chat configurado.")

# Función para la tarea programada
async def scheduled_task(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje programado al chat y verifica alertas de precios"""
    global telegram_bot, db
    if telegram_bot is None:
        telegram_bot = TelegramBot()
    if db is None:
        db = CryptoDatabase()
    
    # Obtener configuración desde variables de entorno
    from src.bot import CRYPTO_DEFAULT_PRICE_SOURCE, CRYPTO_NOTIFICATION_COOLDOWN
    
    # Aquí se implementaría la lógica para verificar precios y disparar alertas
    # usando los valores de configuración del archivo config.env
    
    # Usar la clase TelegramBot para enviar el mensaje
    telegram_bot.send_message("🔔 Ejecución programada - Verificando alertas de precios")

# Función para crear una alerta
async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Crea una alerta para un token a un precio objetivo"""
    global db
    if db is None:
        db = CryptoDatabase()
    
    # Obtener configuración desde variables de entorno
    from src.bot import CRYPTO_MAX_ALERTS_PER_TOKEN
    
    # Verificar que se proporcionaron los argumentos necesarios
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "❌ <b>Error:</b> Formato incorrecto.\n\n"
            "<b>Uso:</b> /alert <token_name> <alert_type> <target_price> [token_contract]\n\n"
            "<b>Ejemplo:</b> /alert BTC above 50000\n"
            "<b>Ejemplo:</b> /alert ETH below 3000\n"
            "<b>Ejemplo:</b> /alert PEPE above 0.000001 0x6982508145454ce325ddbe47a25d4ec3d2311933",
            parse_mode='HTML'
        )
        return
    
    # Extraer los parámetros
    token_name = context.args[0].upper()
    alert_type = context.args[1].lower()
    
    # Validar el tipo de alerta
    if alert_type not in ['above', 'below']:
        await update.message.reply_text(
            "❌ <b>Error:</b> El tipo de alerta debe ser 'above' o 'below'.",
            parse_mode='HTML'
        )
        return
    
    # Validar y convertir el precio objetivo
    try:
        target_price = float(context.args[2])
        if target_price <= 0:
            raise ValueError("El precio debe ser mayor que cero")
    except ValueError:
        await update.message.reply_text(
            "❌ <b>Error:</b> El precio objetivo debe ser un número válido mayor que cero.",
            parse_mode='HTML'
        )
        return
    
    # Verificar si se proporcionó un contrato de token (opcional)
    token_contract = None
    if len(context.args) >= 4:
        token_contract = context.args[3]
    
    # Verificar si el usuario ya tiene demasiadas alertas para este token
    token_alerts = db.get_alerts_by_token(token_name)
    active_alerts = [alert for alert in token_alerts if alert['is_active']]
    
    if len(active_alerts) >= CRYPTO_MAX_ALERTS_PER_TOKEN:
        await update.message.reply_text(
            f"❌ <b>Error:</b> Ya tienes {len(active_alerts)} alertas activas para {token_name}. "  
            f"El máximo permitido es {CRYPTO_MAX_ALERTS_PER_TOKEN}.",
            parse_mode='HTML'
        )
        return
    
    # Añadir la alerta a la base de datos
    try:
        alert_id = db.add_alert(token_name, alert_type, target_price, token_contract)
        
        # Mensaje de confirmación
        confirmation = f"✅ <b>Alerta creada:</b>\n\n"
        confirmation += f"<b>ID:</b> {alert_id}\n"
        confirmation += f"<b>Token:</b> {token_name}\n"
        if token_contract:
            confirmation += f"<b>Contrato:</b> {token_contract}\n"
        confirmation += f"<b>Tipo:</b> {'Por encima de' if alert_type == 'above' else 'Por debajo de'}\n"
        confirmation += f"<b>Precio objetivo:</b> {target_price}\n"
        confirmation += f"<b>Creada:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await update.message.reply_text(confirmation, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error al crear alerta: {e}")
        await update.message.reply_text(
            f"❌ <b>Error:</b> No se pudo crear la alerta. {str(e)}",
            parse_mode='HTML'
        )

async def post_init(application: Application) -> None:
    """Configura los comandos que aparecerán en el teclado de Telegram"""
    commands = [
        BotCommand("ping", "Comprueba si el bot está activo"),
        BotCommand("status", "Muestra información del sistema"),
        BotCommand("report", "Envía un informe detallado usando TelegramBot"),
        BotCommand("scheduled", "Muestra las alertas de precio programadas"),
        BotCommand("alert", "Crea una alerta de precio para un token"),
        #BotCommand("list", "Muestra todas las alertas de precio"),
        BotCommand("remove", "Elimina una alerta de precio por ID")
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Comandos de teclado configurados")

# Función para inicializar las instancias globales
def init_telegram_bot():
    """Inicializa las instancias globales del bot de Telegram y la base de datos"""
    global telegram_bot, db
    telegram_bot = TelegramBot()
    db = CryptoDatabase()
    logger.info("Instancias de TelegramBot y CryptoDatabase inicializadas")
    return telegram_bot