import sqlite3
import sys

def check_db(db_path):
    try:
        print(f'\nVerificando banco: {db_path}')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar sintomas
        cursor.execute('SELECT COUNT(*) FROM signs')
        signs_count = cursor.fetchone()[0]
        print(f'Número de sintomas: {signs_count}')
        
        # Verificar síndromes
        cursor.execute('SELECT COUNT(*), GROUP_CONCAT(syndrome_name) FROM syndromes')
        syndromes_info = cursor.fetchone()
        print(f'Número de síndromes: {syndromes_info[0]}')
        print('Nomes das síndromes:')
        if syndromes_info[1]:
            for syndrome in syndromes_info[1].split(','):
                print(f'- {syndrome}')
        
        conn.close()
        return True
    except Exception as e:
        print(f'Erro ao verificar banco: {e}')
        return False

if __name__ == '__main__':
    db_paths = [
        r'C:\Users\fagun\louis-ml\data\syndrome_data.db',
        r'C:\Users\fagun\louis-ml\data\syndrome_data.db.bak',
        r'C:\Users\fagun\louis-ml - Copia\data\syndrome_data.db',
        r'C:\Users\fagun\OneDrive\Desktop\louiS_2.0\syndrome_data.db',
        r'C:\Users\fagun\louis_streamlit\syndrome_data.db',
        r'C:\Users\fagun\louis-backup\syndrome_data.db'
    ]
    
    for path in db_paths:
        check_db(path)
