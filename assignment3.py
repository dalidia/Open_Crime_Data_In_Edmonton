import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import numpy as np

# connects database 
def connect(path):
    conn = sqlite3.connect(path)
    c =conn.cursor()
    c.execute('PRAGMA foreign_keys=ON; ')
    conn.commit()
    return conn, c

# display all papers in pages with each displayed page having 5 papers
def display_pages(conn, c):
    df = pd.read_sql_query("SELECT title FROM papers;", conn)

    size = len(df)
    first_page = 0
    last_page = 5
    print(df.iloc[:last_page,0:1])
    selection =''

    # Show all papers until indicate it to quit
    while (True):
        print("\nSelect 'n' for next page, 'p' for previous or 'q' to quit")
        selection = input(">")
        # go to next page
        if selection.upper() == 'N':
            if (last_page) >= size:
                print("Page does not exist. Try again.")
            else :
                first_page = last_page
                last_page += 6
                print(df.iloc[first_page:last_page])
        # go to previous page
        elif selection.upper() == 'P':
            if (first_page) <= 0:
                print("Page does not exist. Try again.")
            else:
                first_page -=5
                last_page -=6
                print(df.iloc[first_page:last_page])
        # quit
        elif selection.upper() == "Q":
            break
        else:
            print("Invalid input. Try again.")
    
    conn.commit()
    return df

def get_valid_input(conn,c):
    df = display_pages(conn, c)
    print("\nChoose the index of the paper to be selected")

    # get valid input
    while True:
        try:
            paper_ind = int(input(">"))
            break
        except Exception as e:
            print("Invalid input. Please, try again")
            continue
    
    return df, paper_ind

# show all papers 
def show_current_reviewers(conn, c):
    df, paper_ind = get_valid_input(conn,c)
    
    title_to_be = list(df.iloc[paper_ind])
    p_title= (title_to_be[0],)
    # allow one paper to be selected
    c.execute("select reviewer from papers p, reviews r where p.id=r.paper and p.title=?;",p_title)
    rows = c.fetchall()
    size_rows = len(rows)

    try:
        # display the email of all reviewers that have reviewed the paper
        for i in range(0,size_rows):
           print(rows[i][0])
    except Exception as e:
        #if empty
        print("Reviewer not assigned")
    
    conn.commit()
    return

def show_potential_reviewers(conn, c):
    df, paper_ind = get_valid_input(conn, c)
    title_to_be = list(df.iloc[paper_ind])
    p_title = (title_to_be[0],title_to_be[0])
    c.execute('''select reviewer from papers p, expertise e where p.area=e.area and p.title=? 
            EXCEPT select reviewer from papers p, reviews r 
            where p.id=r.paper and p.title=?;''', p_title)
   
    rows = c.fetchall()
    size_rows = len(rows)
    
    try:
        # display the email of all reviewers that have reviewed the paper
        for i in range(0,size_rows):
           print(rows[i][0])
    except Exception as e:
        # if empty
        print("Potential reviewers not assigned")
    
    reviewer = input("Choose a reviewer")
    orig, imp, sound = input("\nInput scores for originality, importance and soundness: ").split()
    c.execute('''UPDATE reviews
            SET originality = ?, importance = ?, soundness = ?
            WHERE reviewer = ?''', orig, imp, sound, reviewer)

    conn.commit()
    return

def get_reviews_in_range(conn, c):
    lb = 0
    ub = 0
    while True:
        try:
            lb = int(input("Enter a bound: "))
            ub = int(input("Enter another bound: "))
        except Exception as e:
            print("\nInvalid bound. Please try again.")
            continue
        if lb > ub:
            tmp = ub
            ub = lb
            lb = tmp
        break

    query = '''
    select reviewer as rv
    from 
        (select reviewer, count(*) as C 
        from reviews 
        group by reviewer 
        union 
        select email as reviewer, 0 as C 
        from users U 
        where U.email not in (select reviewer from reviews)) 
    where C >= ''' + str(lb) + " and " + " C <= " + str(ub) + ";"

    reviews = pd.read_sql(query, conn)["rv"].tolist()
    print("\nReviewers with #reviews between " + str(lb) + " and " + str(ub) + ':')
    for r in reviews:
        print(r)
    conn.commit()
    return

def show_author_participation(conn, c):
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

        print("Provide the author\n")
        author = input(">")
        
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

def most_popular_areas(conn, c):
    query = '''
    select area, count(*) as C 
    from papers 
    group by area
    union 
    select name as area, 0 as C 
    from areas A 
    where A.name not in (select area from papers)
    order by C desc;'''

    df = pd.read_sql(query, conn)
    areas = df["area"].tolist()
    counts = df["C"].tolist()

    # Finds the 5 most popular areas as well as any other areas with the same popularity as areas in the top 5.
    i = 0
    j = 0
    prev = None
    while i < 5 and j < len(counts):
        if counts[j] != prev:
            prev = counts[j]
            i += 1
        j += 1

    areas = areas[:j]
    counts = counts[:j]
        
    #print(areas)
    #print(counts)
    print("Generating piechart of the 5 most popular areas:")
    plt.pie(counts, labels=areas, autopct="%1.1f%%")
    plt.title("Most Popular Areas")
    plt.show()
    conn.commit()
    return

def show_avg_review_scores(conn,c):
    query = ''' SELECT reviewer, AVG(ORIGINALITY)as originality, AVG(IMPORTANCE) as importance,
			    AVG(SOUNDNESS) as soundness
                FROM reviews r, papers p
                WHERE  r.paper = p.id
                GROUP BY reviewer '''
    df = pd.read_sql_query(query, conn)
    index = ['Anakin', 'C3P0','Darth','Donald','Mickey','Minnie','Pluto','R2D2','Tom']
    df2 = pd.DataFrame(df, columns=['originality', 'importance', 'soundness']) 
    df2.plot.bar()
    plt.plot()
    plt.show()
 
    conn.commit()
    return 
    
def main():
    while True:
        try:
    	    conn, c = connect(input("Enter the name of the database: "))
        except:
            print("Incorrect input. Please try again.")
            continue
        break

    functions = [show_current_reviewers, show_potential_reviewers, get_reviews_in_range, show_author_participation, most_popular_areas]
    fn_select = "\nInput a number to select a function, or q to quit:"
    while True:
        print(fn_select)
        for i in range(0, len(functions)):
            print(str(i) + ': ' + functions[i].__name__)
        input_str = input("\n> ")
        if input_str == 'q':
            break
        else:
            try:
                fn = functions[int(input_str)]
            except Exception as e:
                print("\nInvalid input, please try again.")
                continue
            fn(conn, c)
    conn.commit()
    conn.close()

main()
