import sqlite3
import logging
import json
import unicodedata
import streamlit as st
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_path():
    """Get the database path based on the environment"""
    if 'STREAMLIT_SHARING_MODE' in os.environ:
        return os.path.join('/mount/src/louis-ml/data', 'syndrome_data.db')
    else:
        return Path(__file__).parent.parent.parent / "data" / "syndrome_data.db"

def get_db_connection():
    """Create database connection"""
    try:
        db_path = get_db_path()
        if not os.path.exists(db_path):
            logger.error(f"Database file not found at: {db_path}")
            return None
        conn = sqlite3.connect(db_path)
        logger.info(f'SQLite connection established successfully at {db_path}')
        return conn
    except sqlite3.Error as e:
        logger.error(f'Error connecting to SQLite: {e}')
        return None

@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_symptoms():
    logger.debug("Carregando sintomas do banco de dados.")
    conn = get_db_connection()
    if conn:
        try:
            query = "SELECT DISTINCT signs FROM syndromes"
            cursor = conn.execute(query)
            all_signs = cursor.fetchall()
            
            symptoms_set = set()
            for signs_tuple in all_signs:
                sign = signs_tuple[0].strip()
                normalized_sign = unicodedata.normalize('NFD', sign).encode('ascii', 'ignore').decode('utf-8').lower()
                symptoms_set.add((sign, normalized_sign))
            
            symptoms = sorted([s[0] for s in symptoms_set])
            logger.debug(f"{len(symptoms)} sintomas únicos carregados.")
            return symptoms
        except Exception as e:
            logger.error(f"Erro ao processar sintomas: {e}")
            return []
        finally:
            conn.close()
    return []

@st.cache_data
def load_syndromes():
    logger.debug("Carregando todas as síndromes do banco de dados.")
    conn = get_db_connection()
    if conn:
        try:
            query = """
                SELECT syndrome_name, signs, locals, arteries, 
                       notes, is_ipsilateral, local_name, vessel_name 
                FROM syndromes
            """
            cursor = conn.execute(query)
            syndromes = cursor.fetchall()
            
            processed_syndromes = []
            for row in syndromes:
                syndrome = {
                    "syndrome_name": row[0],
                    "signs": json.loads(row[1]),
                    "locals": row[2],
                    "arteries": row[3],
                    "notes": row[4],
                    "is_ipsilateral": row[5],
                    "local_name": row[6],
                    "vessel_name": row[7]
                }
                processed_syndromes.append(syndrome)
            return processed_syndromes
        except Exception as e:
            logger.error(f"Erro ao processar síndromes: {e}")
            return []
        finally:
            conn.close()
    return []