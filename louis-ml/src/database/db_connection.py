import sqlite3
import logging
from pathlib import Path

DB_PATH = r"C:\Users\fagun\OneDrive\Desktop\louiS_2.0\syndrome_data.db"

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco: {e}")
        return None

def load_symptoms():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM symptoms")
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Erro ao carregar sintomas: {e}")
            return None
        finally:
            conn.close()
    return None

def load_syndromes():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM syndromes")
            return [
                {
                    'syndrome_name': row[1],
                    'signs': row[2].split(','),
                    'locals': row[3],
                    'arteries': row[4],
                    'notes': row[5]
                }
                for row in cursor.fetchall()
            ]
        except Exception as e:
            logging.error(f"Erro ao carregar síndromes: {e}")
            return None
        finally:
            conn.close()
    return None