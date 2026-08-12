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
    conn.close()

def load_products() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT nazwa, bialko, tluszcze, weglowodany, kalorie FROM products""")
    rows = cursor.fetchall()
    conn.close()

    products = []
    for row in rows:
        product = {
            "nazwa": row[0],
            "bialko": row[1],
            "tluszcze": row[2],
            "weglowodany": row[3],
            "kalorie": row[4]
        }
        products.append(product)
    return products

def search_products(phrase: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT nazwa, bialko, tluszcze, weglowodany, kalorie FROM products WHERE nazwa LIKE ?""", (f"%{phrase}%",)
    )

    rows = cursor.fetchall()
    conn.close()
    products = []
    for row in rows:
        product = {
            "nazwa": row[0],
            "bialko": row[1],
            "tluszcze": row[2],
            "weglowodany": row[3],
            "kalorie": row[4]
        }
        products.append(product)
    return products



