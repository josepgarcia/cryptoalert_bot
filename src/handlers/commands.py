#!/usr/bin/env python3
import os
import platform
import psutil
import logging
import requests
import time
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

# Variable global para almacenar el tiempo de inicio
start_time = time.time()

# Comandos del bot
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde con 'pong' cuando recibe el comando /ping"""
    # Mantenemos la respuesta directa para comandos interactivos
    await update.message.reply_text('pong')

async def system_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Devuelve información completa del sistema incluyendo uptime y fecha actual"""
    global telegram_bot
    if telegram_bot is None:
        telegram_bot = TelegramBot()
    
    # Calcular uptime
    uptime_seconds = time.time() - start_time
    uptime_days = int(uptime_seconds // 86400)
    uptime_hours = int((uptime_seconds % 86400) // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)
    uptime_seconds_remainder = int(uptime_seconds % 60)
    
    # Formatear uptime
    if uptime_days > 0:
        uptime_str = f"{uptime_days}d {uptime_hours}h {uptime_minutes}m {uptime_seconds_remainder}s"
    elif uptime_hours > 0:
        uptime_str = f"{uptime_hours}h {uptime_minutes}m {uptime_seconds_remainder}s"
    elif uptime_minutes > 0:
        uptime_str = f"{uptime_minutes}m {uptime_seconds_remainder}s"
    else:
        uptime_str = f"{uptime_seconds_remainder}s"
    
    # Obtener información del sistema
    system_info = {
        'Sistema Operativo': platform.system() + ' ' + platform.release(),
        'Versión de Python': platform.python_version(),
        'CPU': platform.processor(),
        'Uso de CPU': f"{psutil.cpu_percent()}%",
        'Memoria RAM': f"{psutil.virtual_memory().percent}% usado ({psutil.virtual_memory().used // (1024**3):.1f}GB / {psutil.virtual_memory().total // (1024**3):.1f}GB)",
        'Disco': f"{psutil.disk_usage('/').percent}% usado",
        'Uptime del Bot': uptime_str,
        'Fecha y Hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Hostname': platform.node()
    }
    
    # Crear mensaje con formato HTML
    message = "🖥️ <b>INFORMACIÓN DEL SISTEMA</b>\n\n"
    for key, value in system_info.items():
        message += f"<b>{key}:</b> {value}\n"
    
    # Añadir información adicional de red
    try:
        # Obtener información de red
        net_io = psutil.net_io_counters()
        message += f"\n<b>Red:</b>\n"
        message += f"• Bytes enviados: {net_io.bytes_sent // (1024**2):.1f} MB\n"
        message += f"• Bytes recibidos: {net_io.bytes_recv // (1024**2):.1f} MB\n"
    except:
        pass
    
    # Añadir información de alertas activas si está disponible
    try:
        global db
        if db is None:
            db = CryptoDatabase()
        
        active_alerts = db.get_active_alerts()
        message += f"\n<b>Alertas Activas:</b> {len(active_alerts)}\n"
    except:
        message += f"\n<b>Alertas Activas:</b> No disponible\n"
    
    # Para respuestas interactivas, seguimos usando el método de la API de python-telegram-bot
    await update.message.reply_text(message, parse_mode='HTML')



# Función para la tarea programada
async def scheduled_task(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje programado al chat y verifica alertas de precios"""
    global telegram_bot, db
    if telegram_bot is None:
        telegram_bot = TelegramBot()
    if db is None:
        db = CryptoDatabase()
    
    # Obtener configuración desde variables de entorno
    from src.bot import CRYPTO_DEFAULT_PRICE_SOURCE, CRYPTO_DEBUG_MODE
    
    # Usar la clase TelegramBot para enviar el mensaje sin formato HTML
    if CRYPTO_DEBUG_MODE:
        telegram_bot.send_message("🔔 Ejecución programada - Verificando alertas de precios", parse_mode=None)
    
    # 1. Obtener todas las alertas activas de la base de datos
    active_alerts = db.get_active_alerts()
    if not active_alerts:
        if CRYPTO_DEBUG_MODE:
            telegram_bot.send_message("ℹ️ No hay alertas activas configuradas.", parse_mode=None)
        return
    
    # 2. Agrupar alertas por token para hacer una sola petición por token
    tokens = {}
    for alert in active_alerts:
        token_name = alert['token_name']
        if token_name not in tokens:
            tokens[token_name] = []
        tokens[token_name].append(alert)
    
    # 3. Hacer las peticiones a CoinGecko para obtener los precios actuales
    token_prices = {}
    triggered_alerts = []
    
    for token_name in tokens.keys():
        try:
            # Convertir el nombre del token a minúsculas para la API
            token_id = token_name.lower()
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if token_id in data and 'usd' in data[token_id]:
                    current_price = data[token_id]['usd']
                    token_prices[token_name] = current_price
                    
                    # 4. Comprobar si las alertas se encuentran above o below
                    for alert in tokens[token_name]:
                        alert_type = alert['alert_type']
                        target_price = alert['target_price']
                        alert_id = alert['id']
                        
                        # Verificar si se cumple la condición de la alerta
                        if (alert_type == 'above' and current_price >= target_price) or \
                           (alert_type == 'below' and current_price <= target_price):
                            # Registrar que la alerta se ha disparado
                            db.trigger_alert(alert_id)
                            triggered_alerts.append({
                                'id': alert_id,
                                'token_name': token_name,
                                'alert_type': alert_type,
                                'target_price': target_price,
                                'current_price': current_price
                            })
                else:
                    telegram_bot.send_message(f"⚠️ No se encontró información de precio para {token_name}", parse_mode=None)
            else:
                telegram_bot.send_message(f"⚠️ Error al consultar precio de {token_name}: Código {response.status_code}", parse_mode=None)
        except Exception as e:
            telegram_bot.send_message(f"⚠️ Error al procesar {token_name}: {str(e)}", parse_mode=None)
    
    # 5. Enviar reporte de alertas disparadas
    if triggered_alerts:
        report = "🚨 ALERTAS DISPARADAS 🚨\n\n"
        for alert in triggered_alerts:
            condition = "por encima de" if alert['alert_type'] == 'above' else "por debajo de"
            report += f"ID: {alert['id']}\n"
            report += f"Token: {alert['token_name']}\n"
            report += f"Condición: {condition} ${alert['target_price']}\n"
            report += f"Precio actual: ${alert['current_price']}\n\n"
        
        telegram_bot.send_message(report, parse_mode=None)
    else:
        if CRYPTO_DEBUG_MODE:
            telegram_bot.send_message("✅ Verificación completada. No se dispararon alertas.", parse_mode=None)

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
        BotCommand("system", "Muestra información completa del sistema"),
        BotCommand("list", "Muestra las alertas de precio programadas"),
        BotCommand("alert", "Crea una alerta de precio para un token"),
        BotCommand("info", "Consulta el precio actual de un token"),
        BotCommand("remove", "Elimina una alerta de precio por ID")
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Comandos de teclado configurados")

# Función para mostrar las alertas programadas
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra las alertas de precio programadas en formato tabla con precios actuales"""
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
    
    # Agrupar alertas por token para hacer una sola petición por token
    tokens = {}
    for alert in active_alerts:
        token_name = alert['token_name']
        if token_name not in tokens:
            tokens[token_name] = []
        tokens[token_name].append(alert)
    
    # Obtener precios actuales de todos los tokens únicos
    token_prices = {}
    for token_name in tokens.keys():
        try:
            # Convertir el nombre del token a minúsculas para la API
            token_id = token_name.lower()
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if token_id in data and 'usd' in data[token_id]:
                    current_price = data[token_id]['usd']
                    token_prices[token_name] = current_price
                else:
                    token_prices[token_name] = "N/A"
            else:
                token_prices[token_name] = "Error"
        except Exception as e:
            logger.error(f"Error al obtener precio de {token_name}: {str(e)}")
            token_prices[token_name] = "Error"
    
    # Crear tabla con formato simple usando tabs
    table_header = "🔔 <b>Alertas de Precio Programadas</b>\n\n"
    #table_header += "<pre>ID\tToken\tTipo\tPrecio Obj.\tPrecio Actual\n"
    #table_header += "──\t─────\t────\t──────────\t────────────\n</pre>"
    
    table_rows = ""
    for alert in active_alerts:
        # Convertir los valores de sqlite3.Row a strings para evitar problemas de formato
        alert_id = str(alert['id'])
        token_name = str(alert['token_name'])
        alert_type = "↑ Above" if str(alert['alert_type']) == 'above' else "↓ Below"
        target_price = str(alert['target_price'])
        
        # Obtener precio actual del token
        current_price = token_prices.get(token_name, "N/A")
        if isinstance(current_price, (int, float)):
            current_price_str = f"${current_price:.2f}"
        else:
            current_price_str = str(current_price)
        
        # Añadir fila con tabs incluyendo el precio actual
        table_rows += f"{alert_id}\t{token_name}\t{alert_type}\t{target_price}$\t [{current_price_str}$]\n"
    
    # Crear mensaje completo
    message = "<pre>" + table_rows + "</pre>\n"
    
    # Enviar la tabla con formato HTML
    await update.message.reply_text(message, parse_mode='HTML')

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
            "Uso: /info <token_name>\n\n"
            "Ejemplo: /info bitcoin\n"
            "Ejemplo: /info ethereum"
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