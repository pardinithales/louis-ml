import sqlite3
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

def get_db_path():
    project_root = Path(__file__).resolve().parent.parent.parent
    db_path = project_root / "data" / "syndrome_data.db"
    return str(db_path)

def get_db_connection():
    try:
        db_path = get_db_path()
        logger.info(f'Caminho do banco de dados: {db_path}')
        conn = sqlite3.connect(db_path)
        logger.info('Conexão com SQLite estabelecida com sucesso')
        return conn
    except sqlite3.Error as e:
        logger.error(f'Erro ao conectar ao SQLite: {e}')
        return None

def load_symptoms():
    """
    Carrega lista única de sintomas do banco de dados
    """
    try:
        conn = sqlite3.connect("data/syndrome_data.db")
        cursor = conn.cursor()
        
        # Pega todos os signs do banco
        cursor.execute("SELECT signs FROM syndromes")
        rows = cursor.fetchall()
        
        all_symptoms = []
        for row in rows:
            try:
                if row[0]:  # verifica se não é None
                    signs = json.loads(row[0])
                    if isinstance(signs, list):
                        all_symptoms.extend([s.strip() for s in signs])
            except (json.JSONDecodeError, AttributeError) as e:
                logging.error(f"Erro ao processar sintomas: {e}")
                continue
        
        # Remove duplicatas mantendo a ordem
        unique_symptoms = list(dict.fromkeys(all_symptoms))
        
        logging.info(f"Sintomas carregados do banco: {unique_symptoms}")
        return unique_symptoms
        
    except sqlite3.Error as e:
        logging.error(f"Erro ao carregar sintomas: {e}")
        return []
    finally:
        if conn:
            conn.close()

def load_syndromes():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.execute('''
                SELECT syndrome_name, signs, locals, arteries, 
                       notes, is_ipsilateral, local_name, vessel_name 
                FROM syndromes
            ''')
            syndromes = []
            for row in cursor.fetchall():
                syndrome = {
                    'syndrome_name': row[0],
                    'signs': row[1].split(',') if row[1] else [],
                    'locals': row[2],
                    'arteries': row[3],
                    'notes': row[4],
                    'is_ipsilateral': bool(row[5]) if row[5] is not None else None,
                    'local_name': row[6],
                    'vessel_name': row[7],
                    'normalized_signs': [s.strip().lower() for s in row[1].split(',')] if row[1] else []
                }
                syndromes.append(syndrome)
            return syndromes
        except Exception as e:
            logger.error(f"Erro ao carregar síndromes: {e}")
            return []
        finally:
            conn.close()
    return []
