import sqlite3
import json
import logging
from pathlib import Path

def get_db_path():
    """Retorna o caminho do banco de dados"""
    db_path = Path(__file__).parent.parent / "data" / "syndromes.db"
    
    # Criar diretório data se não existir
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    return str(db_path)

def get_db_connection():
    """Retorna uma conexão com o banco de dados"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        
        # Inicializar banco se não existir
        init_db()
        
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco: {str(e)}")
        raise

def init_db():
    """Inicializa o banco de dados"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Criar tabela de síndromes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS syndromes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                syndrome_name TEXT NOT NULL UNIQUE,
                signs TEXT,
                locals TEXT,
                arteries TEXT,
                notes TEXT,
                is_ipsilateral TEXT,
                local_name TEXT,
                vessel_name TEXT,
                registered_at TEXT,
                updated_at TEXT
            )
        """)
        
        conn.commit()
        logging.info("✓ Banco de dados inicializado com sucesso")
        
    except Exception as e:
        logging.error(f"Erro ao inicializar banco de dados: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def load_symptoms():
    """Carrega lista de sintomas do banco"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT signs FROM syndromes")
        results = cursor.fetchall()
        
        all_symptoms = set()
        for result in results:
            if result[0]:
                try:
                    signs = json.loads(result[0])
                    all_symptoms.update(signs)
                except json.JSONDecodeError:
                    continue
                    
        return sorted(list(all_symptoms))
    finally:
        conn.close()

def load_syndromes():
    """Carrega todas as síndromes do banco"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                syndrome_name, 
                signs, 
                locals, 
                arteries, 
                notes,
                is_ipsilateral,
                local_name,
                vessel_name,
                registered_at,
                updated_at
            FROM syndromes
        """)
        
        syndromes = []
        for row in cursor.fetchall():
            try:
                syndrome = {
                    'syndrome_name': row[0],
                    'signs': json.loads(row[1]) if row[1] else [],
                    'locals': row[2],
                    'arteries': row[3],
                    'notes': json.loads(row[4]) if row[4] else [],
                    'is_ipsilateral': json.loads(row[5]) if row[5] else {},
                    'local_name': json.loads(row[6]) if row[6] else [],
                    'vessel_name': json.loads(row[7]) if row[7] else [],
                    'registered_at': row[8],
                    'updated_at': row[9]
                }
                syndromes.append(syndrome)
            except json.JSONDecodeError:
                continue
                
        return syndromes
    finally:
        conn.close()
