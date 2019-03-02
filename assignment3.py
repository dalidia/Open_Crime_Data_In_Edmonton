import matplotlib as pb
import sqlite3
import pandas as pd

conn = None
c = None

# connects database 
def connect(path):
    global conn, c
    conn = sqlite3.connect(path)
    c =conn.cursor()
    c.execute('PRAGMA foreign_keys=ON; ')
    conn.commit()
    return

def first_task():
    global conn, c
    df = pd.read_sql_query("SELECT title FROM papers;", conn)
    print(df.iloc[:4])
    return


# selects which questions to run 
def select_options():
    
    pass

def main():
    global conn, c
    path = "a2.db"
    connect(path)
    first_task()

main()