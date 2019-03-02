import matplotlib as pb
import sqlite3
import pandas as pd

conn = None
c = None

# connects database 
def database_name():
    global conn, c
    conn = sqlite3.connect(database)
    c =conn.cursor()
    c.execute('PRAGMA foreign_keys=ON; ')
    conn.commit()
    return

# selects which questions to run 
def select_options():
    
    pass

def main():
    global conn, c
    path = "\movie.db"
    pass

main()