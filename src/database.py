import sqlite3

def get_connection():
    conn = sqlite3.connect("kalkulator.db")
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nazwa TEXT NOT NULL,
        bialko REAL NOT NULL,
        tluszcze REAL NOT NULL,
        weglowodany REAL NOT NULL,
        kalorie REAL NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nazwa TEXT NOT NULL,
        waga REAL NOT NULL,
        bialko REAL NOT NULL,
        tluszcze REAL NOT NULL,
        weglowodany REAL NOT NULL,
        kalorie REAL NOT NULL,
        data TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

def save_product(product: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO products (nazwa, bialko, tluszcze, weglowodany, kalorie)
    VALUES (?, ?, ?, ?, ?)
    """, (
        product['nazwa'],
        product['bialko'],
        product['tluszcze'],
        product['weglowodany'],
        product['kalorie']
    ))

    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id

def save_logs(logs: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO logs (nazwa, waga, bialko, tluszcze, weglowodany, kalorie, data)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        logs['nazwa'],
        logs['waga'],
        logs['bialko'],
        logs['tluszcze'],
        logs['weglowodany'],
        logs['kalorie'],
        logs['data']
    ))

    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id

def load_products() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT id, nazwa, bialko, tluszcze, weglowodany, kalorie FROM products""")
    rows = cursor.fetchall()
    conn.close()

    products = []
    for row in rows:
        product = {
            "id": row[0],
            "nazwa": row[1],
            "bialko": row[2],
            "tluszcze": row[3],
            "weglowodany": row[4],
            "kalorie": row[5]
        }
        products.append(product)
    return products

def load_products_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT id, nazwa, bialko, tluszcze, weglowodany, kalorie FROM products WHERE id = ?""", (product_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    else:
        product = {
                "id": row[0],
                "nazwa": row[1],
                "bialko": row[2],
                "tluszcze": row[3],
                "weglowodany": row[4],
                "kalorie": row[5]
            }
        return product

def load_log_by_date(target_date: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT id, nazwa, waga, bialko, tluszcze, weglowodany, kalorie, data from logs WHERE data = ?""", (target_date,))
    rows = cursor.fetchall()
    conn.close()
    logs = []
    for row in rows:
        log = {
            "id": row[0],
            "nazwa": row[1],
            "waga": row[2],
            "bialko": row[3],
            "tluszcze": row[4],
            "weglowodany": row[5],
            "kalorie": row[6],
            "data": row[7]
        }
        logs.append(log)
    return logs

def search_products(phrase: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, nazwa, bialko, tluszcze, weglowodany, kalorie FROM products WHERE nazwa LIKE ?""", (f"%{phrase}%",)
    )

    rows = cursor.fetchall()
    conn.close()
    products = []
    for row in rows:
        product = {
            "id": row[0],
            "nazwa": row[1],
            "bialko": row[2],
            "tluszcze": row[3],
            "weglowodany": row[4],
            "kalorie": row[5]
        }
        products.append(product)
    return products

def delete_log(log_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""DELETE FROM logs WHERE id = ?""", (log_id,))
    conn.commit()
    conn.close()

def delete_product(log_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""DELETE FROM products WHERE id = ?""", (log_id,))
    conn.commit()
    conn.close()


