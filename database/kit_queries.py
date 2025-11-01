import sqlite3

def search_kit(conn:sqlite3.Connection, name:str=None, scale:str=None, brand:str=None, grade:str=None):
    query = 'SELECT * FROM Kit'
    params = []
    
    if name:
        query += " AND name LIKE ?"
        params.append(f'%{name}%')
    if scale:
        query += ' AND scale = ?'
        params.append(f'{scale}')
    if brand:
        query += ' AND brand = ?'
        params.append(f'{brand}')
    if grade:
        query += ' AND grade = ?'
        params.append(f'{grade}')
        
    cur = conn.cursor()
    cur.execute(query, params)
    return cur.fetchall()