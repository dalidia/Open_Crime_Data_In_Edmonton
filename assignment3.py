import matplotlib.pyplot as plt
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

def display_pages():
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
                print("Page does not exist. Try again.")

            else :
                first_page = last_page
                last_page += 6
                print(df.iloc[first_page:last_page])
            
        elif selection.upper() == 'P':
            if (first_page) <= 0:
                print("Page does not exist. Try again.")
                
            else:
                first_page -=5
                last_page -=6
                print(df.iloc[first_page:last_page])
        else:
            selection = "E"
    
    conn.commit()
    return

def first_task():
    global conn, c
    display_pages()

    paper = (input("Choose the number of the paper to be selected\n"))
    p_title = (paper,)
    # allow one paper to be selected
    c.execute("select reviewer from papers p, reviews r where p.id=r.paper and p.title=?;",p_title)
    rows = c.fetchall()
    size_rows = len(rows)

    if (size_rows == 0):
        print("Reviewer not assigned")
    else:
       for i in range(0,size_rows):
           print(rows[i][0])
    
    conn.commit()
    return

def second_task():
    global conn, c

    display_pages()
    paper = input("Choose the name of the paper to be selected\n")
    p_title = (paper,paper)
    c.execute('''select reviewer from papers p, expertise e where p.area=e.area and p.title=? 
            EXCEPT select reviewer from papers p, reviews r 
            where p.id=r.paper and p.title=?;''', p_title)
    rows = c.fetchall()
    size_rows = len(rows)

    if (size_rows == 0):
        print("Potential reviewers not assigned")
    else:
       for i in range(0,size_rows):
           print(rows[i][0])
    
    conn.commit()
    return

def fourth_task():
    global conn, c

    query = "SELECT author, COUNT(csession) as count FROM papers WHERE decision='A' GROUP BY author"
    df = pd.read_sql_query(query, conn)
    
    while(True):
        option = input('''Select 1 if you want see a barplot of all individual authors and how many sessions they participate in, or 2 if you want to be provided with a number for a selected individual\n''')
        if option == '1' or option == '2':
            break
        print("Your answer is not valid. Please try again.")

    if option == '1':
        # graph the bar plot
        plot = df.plot.bar(x="author")
        plt.plot()
        plt.show()
    else:
        c.execute(query)
        rows = c.fetchall()
        size = len(rows)

        # check if rows is empty SHOULD I PUT THIS???
        if size == 0:
            print("There's no input")

        author = input("Provide the author\n")
        
        found = False
        # look for author
        for i in range(0,size):
            if rows[i][0] == author:
                print(rows[i][1])
                found = True
        
        if(not found):
            print("Author could not be found. Invalid author.")

    conn.commit()
    return

# selects which questions to run 
def select_options():
    
    pass

def main():
    global conn, c
    path = "a2.db"
    connect(path)
    first_task()
    second_task()
    #fourth_task()

    conn.commit()
    conn.close()

main()