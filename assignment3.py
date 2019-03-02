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
    size = len(df)
    first_page = 0
    last_page = 5
    print(df.iloc[:last_page,0:1])
    selection =''

    # Show all papers
    while (selection != 'E'):
        selection = input("Select 'N' for next page, 'P' for previous or 'E' to exit\n")
        if selection.upper() == 'N':
            if (last_page) >= size:
                print("Page does not exist")

            else :
                first_page = last_page
                last_page += 6
                print(df.iloc[first_page:last_page])
            
        elif selection.upper() == 'P':
            if (first_page) <= 0:
                print("Page does not exist")
                
            else:
                first_page -=5
                last_page -=6
                print(df.iloc[first_page:last_page])
        else:
            selection = "E"

    # allow one paper to be selected
    paper = (input("Choose the number of the paper to be selected\n"))
    p_title = (paper,)
    c.execute("select reviewer from papers p, reviews r where p.id=r.paper and p.title=?;",p_title)
    rows = c.fetchall()
    size_rows = len(rows)

    if (size_rows == 0):
        print("Reviewer not assigned")
    else:
       for i in range(0,size_rows):
           print(rows[i][0])


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