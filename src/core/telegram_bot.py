#!/usr/bin/env python3
"""
Script para enviar mensajes por Telegram usando variables de entorno
"""

import os
import requests
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class TelegramBot:
    """Clase para manejar el envío de mensajes por Telegram"""

    def __init__(self, config_file: str = None):
        """
        Inicializa el bot de Telegram

        Args:
            config_file (str): Ruta al archivo de configuración
        """
        # Cargar variables de entorno desde el archivo de configuración
        if config_file is None:
            from pathlib import Path
            config_file = Path(__file__).parent.parent.parent / 'config' / 'config.env'
        load_dotenv(config_file)

        # Obtener configuración desde variables de entorno
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.parse_mode = os.getenv("TELEGRAM_PARSE_MODE", "HTML")
        self.disable_web_page_preview = os.getenv(
            "TELEGRAM_DISABLE_WEB_PAGE_PREVIEW", "false").lower() == "true"
        self.disable_notification = os.getenv(
            "TELEGRAM_DISABLE_NOTIFICATION", "false").lower() == "true"

        # URL base de la API de Telegram
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

        # Validar configuración
        if not self.bot_token or self.bot_token == "tu_token_del_bot_aqui":
            raise ValueError(
                "TELEGRAM_BOT_TOKEN no está configurado correctamente")

        if not self.chat_id or self.chat_id == "tu_chat_id_aqui":
            raise ValueError(
                "TELEGRAM_CHAT_ID no está configurado correctamente")

    def send_message(self,
                     text: str,
                     chat_id: Optional[str] = None,
                     parse_mode: Optional[str] = None,
                     disable_web_page_preview: Optional[bool] = None,
                     disable_notification: Optional[bool] = None,
                     escape_html: bool = False) -> Dict[str, Any]:
        """
        Envía un mensaje por Telegram

        Args:
            text (str): Texto del mensaje
            chat_id (str, optional): ID del chat. Si no se proporciona, usa el de la configuración
            parse_mode (str, optional): Modo de parseo (HTML, Markdown, MarkdownV2)
            disable_web_page_preview (bool, optional): Deshabilitar vista previa de enlaces
            disable_notification (bool, optional): Enviar sin notificación
            escape_html (bool, optional): Si es True, escapa los caracteres especiales HTML

        Returns:
            Dict[str, Any]: Respuesta de la API de Telegram
        """
        # Usar valores por defecto si no se proporcionan
        chat_id = chat_id or self.chat_id
        parse_mode = parse_mode or self.parse_mode
        disable_web_page_preview = disable_web_page_preview if disable_web_page_preview is not None else self.disable_web_page_preview
        disable_notification = disable_notification if disable_notification is not None else self.disable_notification
        
        # Asegurarse de que el texto sea una cadena
        text = str(text)
        
        # Preparar datos del mensaje
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification
        }

        # Enviar mensaje
        response = requests.post(f"{self.base_url}/sendMessage", json=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Error al enviar mensaje: {response.status_code} - {response.text}")

    def send_photo(self,
                   photo_path: str,
                   caption: Optional[str] = None,
                   chat_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Envía una foto por Telegram

        Args:
            photo_path (str): Ruta al archivo de imagen
            caption (str, optional): Pie de foto
            chat_id (str, optional): ID del chat

        Returns:
            Dict[str, Any]: Respuesta de la API de Telegram
        """
        chat_id = chat_id or self.chat_id

        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                "chat_id": chat_id,
                "parse_mode": self.parse_mode
            }

            if caption:
                data["caption"] = caption

            response = requests.post(
                f"{self.base_url}/sendPhoto", data=data, files=files)

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(
                    f"Error al enviar foto: {response.status_code} - {response.text}")

    def send_document(self,
                      document_path: str,
                      caption: Optional[str] = None,
                      chat_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Envía un documento por Telegram

        Args:
            document_path (str): Ruta al archivo
            caption (str, optional): Pie de documento
            chat_id (str, optional): ID del chat

        Returns:
            Dict[str, Any]: Respuesta de la API de Telegram
        """
        chat_id = chat_id or self.chat_id

        with open(document_path, 'rb') as document:
            files = {'document': document}
            data = {
                "chat_id": chat_id,
                "parse_mode": self.parse_mode
            }

            if caption:
                data["caption"] = caption

            response = requests.post(
                f"{self.base_url}/sendDocument", data=data, files=files)

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(
                    f"Error al enviar documento: {response.status_code} - {response.text}")

    def get_me(self) -> Dict[str, Any]:
        """
        Obtiene información del bot

        Returns:
            Dict[str, Any]: Información del bot
        """
        response = requests.get(f"{self.base_url}/getMe")

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Error al obtener información del bot: {response.status_code} - {response.text}")


def main():
    """Función principal para demostrar el uso del bot"""
    try:
        # Crear instancia del bot
        bot = TelegramBot()

        # Obtener información del bot
        bot_info = bot.get_me()
        print(
            f"Bot conectado: {bot_info['result']['first_name']} (@{bot_info['result']['username']})")

        # Ejemplo de envío de mensaje simple
        print("Enviando mensaje de prueba...")
        result = bot.send_message(
            "¡Hola! Este es un mensaje de prueba desde el bot de Python 🐍")
        print(
            f"Mensaje enviado exitosamente. Message ID: {result['result']['message_id']}")

        # Ejemplo de mensaje con formato HTML
        html_message = """
<b>Mensaje con formato HTML</b>
<i>Texto en cursiva</i>
<code>Código inline</code>
<a href="https://python.org">Enlace a Python</a>
        """.strip()

        print("Enviando mensaje con formato HTML...")
        result = bot.send_message(html_message)
        print(
            f"Mensaje HTML enviado exitosamente. Message ID: {result['result']['message_id']}")

    except ValueError as e:
        print(f"Error de configuración: {e}")
        print("Por favor, configura las variables en el archivo config.env")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
