import sqlite3
import discord
from tabulate import tabulate

def format_query_results(cursor, rows):
    col_names = [desc[0] for desc in cursor.description]
    
    str_rows = [[str(v) if v is not None else "NULL" for v in row] for row in rows]
        
    return f"```{tabulate(str_rows, headers=col_names)}```"
    
    