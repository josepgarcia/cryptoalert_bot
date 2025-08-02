#!/usr/bin/env python3
import os
import sqlite3
import logging
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

class CryptoDatabase:
    """Clase para gestionar la base de datos de alertas de criptomonedas"""
    
    def __init__(self, db_path=None):
        """Inicializa la conexión a la base de datos y crea las tablas si no existen"""
        if db_path is None:
            from pathlib import Path
            db_path = Path(__file__).parent.parent.parent / 'data' / 'crypto_alerts.db'
            # Asegurar que el directorio data existe
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Crear la base de datos y las tablas si no existen
        self._connect()
        self._create_tables()
        
        logger.info(f"Base de datos inicializada en {db_path}")
    
    def _connect(self):
        """Establece la conexión con la base de datos"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            raise
    
    def _create_tables(self):
        """Crea las tablas necesarias si no existen"""
        try:
            # Tabla de alertas
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_name TEXT NOT NULL,
                token_contract TEXT,
                alert_type TEXT NOT NULL,  -- 'above' o 'below'
                target_price REAL NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_triggered TIMESTAMP,
                trigger_count INTEGER DEFAULT 0
            )
            ''')
            
            # Tabla para historial de precios
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_name TEXT NOT NULL,
                price REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error al crear las tablas: {e}")
            self.conn.rollback()
            raise
    
    def add_alert(self, token_name, alert_type, target_price, token_contract=None):
        """Añade una nueva alerta a la base de datos"""
        try:
            # Validar el tipo de alerta
            if alert_type not in ['above', 'below']:
                raise ValueError("El tipo de alerta debe ser 'above' o 'below'")
            
            # Insertar la alerta
            self.cursor.execute('''
            INSERT INTO alerts (token_name, token_contract, alert_type, target_price)
            VALUES (?, ?, ?, ?)
            ''', (token_name.upper(), token_contract, alert_type, target_price))
            
            alert_id = self.cursor.lastrowid
            self.conn.commit()
            
            logger.info(f"Alerta creada: {token_name} {alert_type} {target_price}")
            return alert_id
        except sqlite3.Error as e:
            logger.error(f"Error al añadir alerta: {e}")
            self.conn.rollback()
            raise
    
    def get_active_alerts(self):
        """Obtiene todas las alertas activas"""
        try:
            self.cursor.execute('''
            SELECT * FROM alerts WHERE is_active = 1
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error al obtener alertas activas: {e}")
            raise
    
    def get_alerts_by_token(self, token_name):
        """Obtiene todas las alertas para un token específico"""
        try:
            self.cursor.execute('''
            SELECT * FROM alerts WHERE token_name = ? ORDER BY created_at DESC
            ''', (token_name.upper(),))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error al obtener alertas para {token_name}: {e}")
            raise
    
    def update_alert_status(self, alert_id, is_active):
        """Actualiza el estado de una alerta"""
        try:
            self.cursor.execute('''
            UPDATE alerts SET is_active = ? WHERE id = ?
            ''', (1 if is_active else 0, alert_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error al actualizar estado de alerta {alert_id}: {e}")
            self.conn.rollback()
            raise
    
    def trigger_alert(self, alert_id):
        """Marca una alerta como disparada"""
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute('''
            UPDATE alerts 
            SET last_triggered = ?, trigger_count = trigger_count + 1 
            WHERE id = ?
            ''', (now, alert_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error al disparar alerta {alert_id}: {e}")
            self.conn.rollback()
            raise
    
    def delete_alert(self, alert_id):
        """Elimina una alerta de la base de datos"""
        try:
            self.cursor.execute('''
            DELETE FROM alerts WHERE id = ?
            ''', (alert_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error al eliminar alerta {alert_id}: {e}")
            self.conn.rollback()
            raise
    
    def remove_alert(self, alert_id):
        """Alias para delete_alert"""
        return self.delete_alert(alert_id)
        
    def get_all_alerts(self):
        """Obtiene todas las alertas de la base de datos"""
        try:
            self.cursor.execute('''
            SELECT * FROM alerts ORDER BY token_name, created_at DESC
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error al obtener todas las alertas: {e}")
            raise
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            logger.info("Conexión a la base de datos cerrada")
    
    def __del__(self):
        """Destructor que asegura que la conexión se cierre"""
        self.close()
    



if __name__ == "__main__":
    # Configurar logging para pruebas
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    print("Este módulo proporciona funcionalidad para gestionar la base de datos de alertas de criptomonedas.")
    print("Importa la clase CryptoDatabase para utilizarla en tu aplicación.")