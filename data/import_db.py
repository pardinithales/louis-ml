# import_db.py
import sqlite3
import json

def import_from_json():
    # Lê o JSON
    with open('database_backup.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Conecta ao banco
    conn = sqlite3.connect("syndrome_data.db")
    cursor = conn.cursor()
    
    # Insere dados
    for item in data:
        columns = ', '.join(item.keys())
        placeholders = ', '.join(['?' for _ in item])
        query = f"INSERT INTO syndromes ({columns}) VALUES ({placeholders})"
        cursor.execute(query, list(item.values()))
    
    conn.commit()
    print(f"Importados {len(data)} registros")

if __name__ == "__main__":
    import_from_json()