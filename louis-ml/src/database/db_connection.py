import sqlite3
import logging
import streamlit as st
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_path():
    try:
        # Tenta pegar do secrets primeiro
        return st.secrets["database"]["PATH"]
    except:
        # Fallback para caminho local
        return Path(__file__).parent.parent.parent / "data" / "syndrome_data.db"

def get_db_connection():
    try:
        conn = sqlite3.connect(get_db_path())
        logger.info("Conexão com SQLite estabelecida com sucesso")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao SQLite: {e}")
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