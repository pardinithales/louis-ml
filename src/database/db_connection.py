import sqlite3
import json
import logging
from pathlib import Path

def get_db_path():
    """Retorna o caminho do banco de dados"""
    db_path = Path(__file__).parent.parent.parent / "data" / "syndrome_data.db"
    logging.info(f"Tentando acessar banco em: {db_path}")
    
    if not db_path.exists():
        logging.warning(f"Banco não encontrado em: {db_path}")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
    return str(db_path)

def init_db():
    """Inicializa o banco de dados"""
    try:
        # Conectar diretamente sem usar get_db_connection
        conn = sqlite3.connect(get_db_path())
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
        return True
        
    except Exception as e:
        logging.error(f"Erro ao inicializar banco de dados: {str(e)}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

def get_db_connection():
    """Retorna uma conexão com o banco de dados"""
    try:
        db_path = get_db_path()
        logging.info(f"Conectando ao banco: {db_path}")
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco: {str(e)}")
        raise

def load_symptoms():
    """Carrega lista de sintomas do banco"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT signs FROM syndromes")
        results = cursor.fetchall()
        
        if not results:
            logging.warning("Nenhum sintoma encontrado no banco")
            return []
            
        all_symptoms = set()
        for result in results:
            if result[0]:
                try:
                    signs = json.loads(result[0])
                    all_symptoms.update(signs)
                except json.JSONDecodeError as e:
                    logging.error(f"Erro ao decodificar sintomas: {str(e)}")
                    continue
                    
        return sorted(list(all_symptoms))
        
    except Exception as e:
        logging.error(f"Erro ao carregar sintomas: {str(e)}")
        return []
        
    finally:
        if 'conn' in locals():
            conn.close()

def load_syndromes():
    """Carrega todas as síndromes do banco"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Primeiro, vamos ver a estrutura da tabela
        cursor.execute("PRAGMA table_info(syndromes)")
        columns = cursor.fetchall()
        logging.info(f"Estrutura da tabela: {columns}")
        
        cursor.execute("SELECT * FROM syndromes")
        results = cursor.fetchall()
        
        if not results:
            logging.warning("Nenhuma síndrome encontrada no banco")
            return []
            
        # Log do primeiro resultado para debug
        if results:
            logging.info(f"Exemplo de registro: {results[0]}")
            
        syndromes = []
        for row in results:
            try:
                # Mapear colunas dinamicamente
                syndrome = {}
                
                for i, col in enumerate(columns):
                    col_name = col[1]  # Nome da coluna
                    if i < len(row):  # Verificar se o índice existe
                        value = row[i]
                        
                        # Tentar converter JSON se necessário
                        if col_name in ['signs', 'notes', 'is_ipsilateral', 'local_name', 'vessel_name']:
                            try:
                                value = json.loads(value) if value else []
                            except:
                                value = []
                                
                        syndrome[col_name] = value
                
                syndromes.append(syndrome)
                
            except Exception as e:
                logging.error(f"Erro ao processar síndrome: {str(e)}")
                logging.error(f"Row problemática: {row}")
                continue
                
        return syndromes
        
    except Exception as e:
        logging.error(f"Erro ao carregar síndromes: {str(e)}")
        return []
        
    finally:
        if 'conn' in locals():
            conn.close()
