import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Usando o caminho absoluto do banco original
DB_PATH = r"C:\Users\fagun\OneDrive\Desktop\louiS_2.0\syndrome_data.db"

def test_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='syndromes'
        """)
        if not cursor.fetchone():
            logger.error("Tabela 'syndromes' não encontrada!")
            return False
            
        # Verificar contagem de registros
        cursor.execute("SELECT COUNT(*) FROM syndromes")
        count = cursor.fetchone()[0]
        logger.info(f"Total de síndromes: {count}")
        
        # Verificar primeira síndrome
        cursor.execute("""
            SELECT syndrome_name, signs, locals, arteries 
            FROM syndromes LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            logger.info(f"Primeira síndrome: {row[0]}")
            logger.info(f"Sintomas: {row[1]}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao verificar banco: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_db() 