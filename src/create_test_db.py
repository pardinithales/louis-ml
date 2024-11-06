import sqlite3
import json
import os
from pathlib import Path

def create_database():
    # Caminho do banco de dados
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    db_path = project_root / 'data' / 'syndrome_data.db'
    
    print(f'Criando banco de dados em: {db_path}')

    # Garantir que o diretório existe
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Criar conexão
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Criar tabelas
    cursor.execute('DROP TABLE IF EXISTS signs')
    cursor.execute('DROP TABLE IF EXISTS syndromes')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS signs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sign TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS syndromes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        syndrome_name TEXT NOT NULL,
        signs TEXT NOT NULL,
        locals TEXT,
        arteries TEXT,
        notes TEXT,
        is_ipsilateral BOOLEAN,
        local_name TEXT,
        vessel_name TEXT
    )
    ''')

    # Dados de teste - Sintomas
    test_signs = [
        'headache',
        'weakness',
        'numbness',
        'visual loss',
        'diplopia',
        'ataxia',
        'dysarthria',
        'vertigo',
        'nausea',
        'vomiting',
        'hemiparesis',
        'hemianopsia',
        'facial palsy',
        'dysphagia',
        'aphasia'
    ]

    # Inserir sintomas
    for sign in test_signs:
        cursor.execute('INSERT OR IGNORE INTO signs (sign) VALUES (?)', (sign,))

    # Dados de teste - Síndromes
    test_syndromes = [
        {
            'name': 'Lateral Medullary Syndrome',
            'signs': 'vertigo,ataxia,nausea,dysphagia',
            'locals': 'Lateral medulla',
            'arteries': 'Posterior inferior cerebellar artery'
        },
        {
            'name': 'Weber Syndrome',
            'signs': 'weakness,diplopia,visual loss',
            'locals': 'Midbrain',
            'arteries': 'Posterior cerebral artery'
        },
        {
            'name': 'Middle Cerebral Artery Syndrome',
            'signs': 'hemiparesis,aphasia,hemianopsia',
            'locals': 'MCA territory',
            'arteries': 'Middle cerebral artery'
        },
        {
            'name': 'Anterior Cerebral Artery Syndrome',
            'signs': 'weakness,numbness',
            'locals': 'ACA territory',
            'arteries': 'Anterior cerebral artery'
        },
        {
            'name': 'Posterior Cerebral Artery Syndrome',
            'signs': 'visual loss,headache',
            'locals': 'PCA territory',
            'arteries': 'Posterior cerebral artery'
        }
    ]

    # Inserir síndromes
    for syndrome in test_syndromes:
        cursor.execute('''
        INSERT OR IGNORE INTO syndromes 
        (syndrome_name, signs, locals, arteries) 
        VALUES (?, ?, ?, ?)
        ''', (
            syndrome['name'],
            syndrome['signs'],
            syndrome['locals'],
            syndrome['arteries']
        ))

    # Commit e fechar
    conn.commit()
    conn.close()
    print('Banco de dados criado com sucesso!')

if __name__ == '__main__':
    create_database()
