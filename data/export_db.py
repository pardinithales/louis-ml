import sqlite3
import json

def export_to_json():
    try:
        # Conecta ao banco atual
        conn = sqlite3.connect("syndrome_data.db")
        cursor = conn.cursor()
        
        # Pega todos os dados
        cursor.execute("SELECT * FROM syndromes")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # Converte para lista de dicionários
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
            
        # Salva em JSON
        with open('database_backup.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✓ Exportados {len(data)} registros com sucesso")
        
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    export_to_json()