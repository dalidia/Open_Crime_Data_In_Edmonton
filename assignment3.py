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
    pass

# selects which questions to run 
def select_options():
    
    pass

def main():
    global conn, c
    database = input("Input the name of the database\n")
    pass

main()