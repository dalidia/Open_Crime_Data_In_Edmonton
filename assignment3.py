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

# get valid input and returns the index of a paper and
def get_valid_input(conn,c):
    df = display_pages(conn, c)
    print("\nChoose the index of the paper to be selected, or press 'q' to quit.")
    
    # find the number of papers 
    c.execute('''SELECT COUNT(id) FROM papers''')
    paper_range = c.fetchone()
    paper_range = paper_range[0]
    while True:
        try:
            paper_ind = input(">")
            if paper_ind.upper() == "Q":
                break
            paper_ind = int(paper_ind)
            if paper_ind < paper_range and paper_ind >= 0:
                break
            else: 
                print("Out of range. Please, try again")
        except Exception as e:
            print("Invalid input. Please, try again")
            continue
    
    return df, paper_ind

# show all papers 
def show_current_reviewers(conn, c):
    df, paper_ind = get_valid_input(conn,c)
    try:
        if paper_ind.upper() == 'Q':
            return
    except:
        pass
    
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
    # display pages
    df, paper_ind = get_valid_input(conn, c)
    try:
        if paper_ind.upper() == 'Q':
            return
    except:
        pass
    title_to_be = list(df.iloc[paper_ind])
    p_title = (title_to_be[0],title_to_be[0])

    # find the potential reviewers
    # reviewers who have already reviewed are not displayed
    c.execute('''select reviewer from papers p, expertise e where p.area=e.area and p.title=? 
            EXCEPT select reviewer from papers p, reviews r 
            where p.id=r.paper and p.title=?;''', p_title)
    
    # store the output of the query in variable rows
    rows = c.fetchall()
    size_rows = len(rows)

    try:
        # display the email of all reviewers that have reviewed the paper
        for i in range(0,size_rows):
           print(rows[i][0])
    except Exception as e:
        # if empty
        print("Potential reviewers not assigned")
    
    # find the author of the paper
    # author is not allowed to review own paper
    paper_title = (title_to_be[0],)
    c.execute("SELECT author FROM papers WHERE title=?;",paper_title)
    author = c.fetchone()
    author = author[0]
    
    # ask for the email of reviewer and check if it is valid
    # this loop continues unless either the user inputs a valid value or
    # or presses 'q' 
    while (True):
        reviewer = input("Choose a reviewer or press 'q' to quit : ")
        if reviewer == author:
            print("\nNot allowed to review this paper. \n")
        elif reviewer not in rows and reviewer.upper() != "Q":
            print("\nNot allowed to review this paper. \n")
        elif  reviewer.upper() == "Q":
            return
        else:
            break

    # take in the values for scores in each category
    print("\nInput scores:")
    orig = int(input("originality:  "))
    imp  = int(input("\nimportance:  "))
    sound = int(input("\nsoundness:  "))

    # calculate the overall score
    overall = (orig+imp+sound)/3
    paper_to = (title_to_be[0],)

    # find the unique paper id corresponding to the title of the chosen paper
    c.execute("SELECT Id FROM papers WHERE title=?",paper_to)
    paper_id = c.fetchone()
    paper_id = paper_id[0]
    insertions = (paper_id,reviewer,orig,imp,sound,overall)

    # insert the new entry into the datbase in table reviews
    c.execute('''INSERT INTO reviews VALUES (?,?,?,?,?,?)''', insertions)
    
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

# show in how many sessions do authors participate in being able to choose 2 options
def show_author_participation(conn, c):
    query = "SELECT author, COUNT(csession) as count FROM papers WHERE decision='A' GROUP BY author"
    df = pd.read_sql_query(query, conn)
    # select valid option
    while True:
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
        print(df.iloc[:,0:1])
        print("\nProvide the index of the author, or press 'q'.")
        
        # check if author is one of the authors who participate
        while True:
            try:
                author_ind = input(">")
                if author_ind.upper() == "Q":
                    break
                elif (list(df.iloc[int(author_ind)])[0] not in df.author.to_string(index=False)):
                    print("Author could not be found. Invalid author. Try again")
                else:
                    author_to_be = list(df.iloc[author_ind])
                    print("The number is ", author_to_be[1])
            except:
                print("Invalid input. Try again.\n")
                continue
        
        

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
        
    # print(areas)
    #print(counts)
    print("Generating piechart of the 5 most popular areas:")
    plt.pie(counts, labels=areas, autopct="%1.1f%%")
    plt.title("Most Popular Areas")
    plt.show()
    conn.commit()
    return

def show_avg_review_scores(conn,c):
    # find the average review scores for each category for each reviwer 
    query = ''' SELECT reviewer, 
                AVG(ORIGINALITY)as originality, 
                AVG(IMPORTANCE) as importance,
			    AVG(SOUNDNESS) as soundness
                FROM reviews r, papers p
                WHERE  r.paper = p.id
                GROUP BY reviewer '''

    df = pd.read_sql_query(query, conn)
    reviewers = list(df.reviewer.to_string(index = 'False'))

    # plot a grouped bar chart
    df2 = pd.DataFrame(df,index = reviewers, columns=['originality', 'importance', 'soundness']) 
    # index =["Anakin@Email","C3P0@Email","Darth@Email",
    # "Donald@Email","Mickey@Email","Minnie@Email","Pluto@Email",
    # "R2D2@Email","Tom@Email"]
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

    functions = [show_current_reviewers, show_potential_reviewers, get_reviews_in_range, show_author_participation, most_popular_areas, show_avg_review_scores]
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
