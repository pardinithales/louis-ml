# db_connection.py
import sqlite3
import logging
import json
import unicodedata
import streamlit as st
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_path():
    # Obter o caminho absoluto para o diretório do projeto
    project_root = Path(__file__).resolve().parent.parent
    db_path = project_root / "data" / "syndrome_data.db"
    return str(db_path)

def get_db_connection():
    try:
        db_path = get_db_path()
        logger.info(f'Caminho do banco de dados: {db_path}')
        conn = sqlite3.connect(db_path)
        logger.info(f'Caminho do banco de dados: {db_path}')
        logger.info('Conexão com SQLite estabelecida com sucesso')
        return conn
    except sqlite3.Error as e:
        logger.error(f'Erro ao conectar ao SQLite: {e}')
        return None

@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_symptoms():
    logger.debug("Carregando sintomas do banco de dados.")
    conn = get_db_connection()
    if conn:
        try:
            query = "SELECT DISTINCT sign FROM signs"
            cursor = conn.execute(query)
            all_signs = cursor.fetchall()
            
            symptoms = [sign[0] for sign in all_signs]
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
def get_db_path():
    # Obter o caminho absoluto para o diretório do projeto
    project_root = Path(__file__).resolve().parent.parent.parent
    db_path = project_root / "data" / "syndrome_data.db"
    return str(db_path)
