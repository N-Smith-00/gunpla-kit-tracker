import sqlite3
from config.config import VALID_SCALES

def search_kit(name:str=None, scale:str=None, brand:str=None, grade:str=None):
    query = 'SELECT * FROM kit_view'
    params = []
    
    if name:
        if len(params) == 0:
            query += " WHERE name LIKE ?"
        else:
            query += " AND name LIKE ?"
        params.append(f'%{name.title()}%')
    if scale and scale in VALID_SCALES:
        if len(params) == 0:
            query += " WHERE scale = ?"
        else:
            query += ' AND scale = ?'
        params.append(f'{scale}')
    if brand:
        if len(params) == 0:
            query += " WHERE brand LIKE ?"
        else:
            query += ' AND brand LIKE ?'
        params.append(f'%{brand.title()}%')
    if grade:
        if len(params) == 0:
            query += f" WHERE grade = ?"
        else:
            query += f' AND grade = ?'
        params.append(f'{grade.upper()}')
        
    return (query, tuple(params))
