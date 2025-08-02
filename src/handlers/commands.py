#!/usr/bin/env python3
import os
import platform
import psutil
import logging
import requests
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
    
    # Usar la clase TelegramBot para enviar el mensaje sin formato HTML
    telegram_bot.send_message("🔔 Ejecución programada - Verificando alertas de precios", parse_mode=None)

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
            "❌ Error: Formato incorrecto.\n\n"
            "Uso: /alert <token_name> <alert_type> <target_price> [token_contract]\n\n"
            "Ejemplo: /alert BTC above 50000\n"
            "Ejemplo: /alert ETH below 3000\n"
            "Ejemplo: /alert PEPE above 0.000001 0x6982508145454ce325ddbe47a25d4ec3d2311933"
        )
        return
    
    # Extraer los parámetros
    token_name = context.args[0].upper()
    alert_type = context.args[1].lower()
    
    # Validar el tipo de alerta
    if alert_type not in ['above', 'below']:
        await update.message.reply_text(
            "❌ Error: El tipo de alerta debe ser 'above' o 'below'."
        )
        return
    
    # Validar y convertir el precio objetivo
    try:
        target_price = float(context.args[2])
        if target_price <= 0:
            raise ValueError("El precio debe ser mayor que cero")
    except ValueError:
        await update.message.reply_text(
            "❌ Error: El precio objetivo debe ser un número válido mayor que cero."
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
            f"❌ Error: Ya tienes {len(active_alerts)} alertas activas para {token_name}. "  
            f"El máximo permitido es {CRYPTO_MAX_ALERTS_PER_TOKEN}."
        )
        return
    
    # Añadir la alerta a la base de datos
    try:
        alert_id = db.add_alert(token_name, alert_type, target_price, token_contract)
        
        # Mensaje de confirmación sin formato HTML
        confirmation = f"✅ Alerta creada:\n\n"
        confirmation += f"ID: {alert_id}\n"
        confirmation += f"Token: {token_name}\n"
        if token_contract:
            confirmation += f"Contrato: {token_contract}\n"
        confirmation += f"Tipo: {'Por encima de' if alert_type == 'above' else 'Por debajo de'}\n"
        confirmation += f"Precio objetivo: {target_price}\n"
        confirmation += f"Creada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await update.message.reply_text(confirmation)
        
    except Exception as e:
        error_str = str(e)
        logger.error(f"Error al crear alerta: {error_str}")
        await update.message.reply_text(
            f"❌ Error: No se pudo crear la alerta. {error_str}"
        )

async def post_init(application: Application) -> None:
    """Configura los comandos que aparecerán en el teclado de Telegram"""
    commands = [
        BotCommand("ping", "Comprueba si el bot está activo"),
        BotCommand("status", "Muestra información del sistema"),
        BotCommand("report", "Envía un informe detallado usando TelegramBot"),
        BotCommand("scheduled", "Muestra las alertas de precio programadas"),
        BotCommand("alert", "Crea una alerta de precio para un token"),
        BotCommand("tokenprice", "Consulta el precio actual de un token"),
        #BotCommand("list", "Muestra todas las alertas de precio"),
        BotCommand("remove", "Elimina una alerta de precio por ID")
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Comandos de teclado configurados")

# Función para mostrar las alertas programadas
async def scheduled_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra las alertas de precio programadas"""
    global db
    if db is None:
        db = CryptoDatabase()
    
    # Obtener todas las alertas activas
    alerts = db.get_all_alerts()
    active_alerts = [alert for alert in alerts if alert['is_active']]
    
    if not active_alerts:
        await update.message.reply_text(
            "ℹ️ Información: No hay alertas de precio programadas."
        )
        return
    
    # Crear mensaje con las alertas sin formato HTML
    message = "🔔 Alertas de precio programadas:\n\n"
    for alert in active_alerts:
        # Convertir los valores de sqlite3.Row a strings para evitar problemas de formato
        alert_id = str(alert['id'])
        token_name = str(alert['token_name'])
        token_contract = str(alert['token_contract']) if alert['token_contract'] else None
        alert_type = str(alert['alert_type'])
        target_price = str(alert['target_price'])
        created_at = str(alert['created_at'])
        
        message += f"ID: {alert_id}\n"
        message += f"Token: {token_name}\n"
        if token_contract:
            message += f"Contrato: {token_contract}\n"
        message += f"Tipo: {'Por encima de' if alert_type == 'above' else 'Por debajo de'}\n"
        message += f"Precio objetivo: {target_price}\n"
        message += f"Creada: {created_at}\n\n"
    
    await update.message.reply_text(message)

# Función para eliminar una alerta
async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Elimina una alerta de precio por ID"""
    global db
    if db is None:
        db = CryptoDatabase()
    
    # Verificar que se proporcionó un ID
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(
            "❌ Error: Formato incorrecto.\n\n"
            "Uso: /remove <alert_id>\n\n"
            "Ejemplo: /remove 1"
        )
        return
    
    # Extraer el ID de la alerta
    try:
        alert_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ Error: El ID de la alerta debe ser un número entero."
        )
        return
    
    # Eliminar la alerta
    try:
        if db.remove_alert(alert_id):
            # Convertir a string para evitar problemas de formato
            alert_id_str = str(alert_id)
            await update.message.reply_text(
                f"✅ Éxito: Alerta con ID {alert_id_str} eliminada correctamente."
            )
        else:
            # Convertir a string para evitar problemas de formato
            alert_id_str = str(alert_id)
            await update.message.reply_text(
                f"❌ Error: No se encontró ninguna alerta con ID {alert_id_str}."
            )
    except Exception as e:
        # Convertir la excepción a string para evitar problemas de formato
        error_str = str(e)
        logger.error(f"Error al eliminar alerta: {error_str}")
        await update.message.reply_text(
            f"❌ Error: No se pudo eliminar la alerta. {error_str}"
        )

# Función para inicializar las instancias globales
def init_telegram_bot():
    """Inicializa las instancias globales del bot de Telegram y la base de datos"""
    global telegram_bot, db
    telegram_bot = TelegramBot()
    db = CryptoDatabase()
    logger.info("Instancias de TelegramBot y CryptoDatabase inicializadas")
    return telegram_bot

# Función para consultar el precio de un token
async def tokenprice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Consulta el precio actual de un token usando la API de CoinGecko"""
    # Verificar que se proporcionó un token
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(
            "❌ Error: Formato incorrecto.\n\n"
            "Uso: /tokenprice <token_name>\n\n"
            "Ejemplo: /tokenprice bitcoin\n"
            "Ejemplo: /tokenprice ethereum"
        )
        return
    
    # Extraer el nombre del token
    token_id = context.args[0].lower()
    
    try:
        # Hacer la petición a la API de CoinGecko
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
        response = requests.get(url)
        
        # Verificar si la respuesta es exitosa
        if response.status_code == 200:
            data = response.json()
            
            # Verificar si el token existe
            if token_id in data:
                price = data[token_id]['usd']
                await update.message.reply_text(
                    f"💰 Precio de {token_id.upper()}: ${price} USD"
                )
            else:
                await update.message.reply_text(
                    f"❌ Error: No se encontró información para el token '{token_id}'."
                )
        else:
            await update.message.reply_text(
                f"❌ Error: No se pudo obtener el precio. Código de estado: {response.status_code}"
            )
    except Exception as e:
        error_str = str(e)
        logger.error(f"Error al consultar precio del token: {error_str}")
        await update.message.reply_text(
            f"❌ Error: No se pudo consultar el precio. {error_str}"
        )