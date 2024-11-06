import sqlite3

def check_data():
    db_path = 'data/syndrome_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print('=== Sintomas ===')
    cursor.execute('SELECT * FROM signs')
    signs = cursor.fetchall()
    for sign in signs:
        print(sign)

    print('\n=== Síndromes ===')
    cursor.execute('SELECT * FROM syndromes')
    syndromes = cursor.fetchall()
    for syndrome in syndromes:
        print(syndrome)

    conn.close()

if __name__ == '__main__':
    check_data()
