import sqlite3


def execute(query: str, db_path: str = './flaskr/static/database/sample.db'):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()

def select(query: str, db_path: str = './flaskr/static/database/sample.db') -> list:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    result = cursor.execute(query)
    return result.fetchall()