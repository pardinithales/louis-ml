import sqlite3
import json

def insert_test_data():
    db_path = 'data/syndrome_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Inserir mais sintomas
    symptoms = [
        'headache', 'weakness', 'numbness', 'visual loss', 'diplopia',
        'ataxia', 'dysarthria', 'vertigo', 'nausea', 'vomiting'
    ]
    
    for symptom in symptoms:
        cursor.execute('INSERT OR IGNORE INTO signs (sign) VALUES (?)', (symptom,))

    # Inserir síndromes de teste
    test_syndromes = [
        {
            'name': 'Lateral Medullary Syndrome',
            'signs': ['vertigo', 'ataxia', 'nausea'],
            'locals': 'Lateral medulla',
            'arteries': 'Posterior inferior cerebellar artery'
        },
        {
            'name': 'Weber Syndrome',
            'signs': ['weakness', 'diplopia', 'visual loss'],
            'locals': 'Midbrain',
            'arteries': 'Posterior cerebral artery'
        }
    ]

    for syndrome in test_syndromes:
        cursor.execute('''
        INSERT OR IGNORE INTO syndromes 
        (syndrome_name, signs, locals, arteries) 
        VALUES (?, ?, ?, ?)
        ''', (
            syndrome['name'],
            json.dumps(syndrome['signs']),
            syndrome['locals'],
            syndrome['arteries']
        ))

    conn.commit()
    conn.close()
    print('Dados de teste inseridos com sucesso!')

if __name__ == '__main__':
    insert_test_data()
