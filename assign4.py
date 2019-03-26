import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import numpy as np
import folium

def connect(path):
    conn = sqlite3.connect(path)
    c =conn.cursor()
    c.execute('PRAGMA foreign_keys=ON; ')
    # conn.commit()
    return conn, c

def get_range_years():
    lb = None
    up = None
    while True:
        try:
            lb = int(input("Enter start year (YYYY): "))
            up = int(input("Enter end year (YYYY): "))
        except:
            print("Invalid bounds. Please try again")
        else:
            if up < lb:
                print("Upper bound is less than lower bound. Please enter bounds again.")
                continue
        break
    return lb, up

def first_n_with_ties(arr, eq, n):
    val = None
    i = n - 1
    if i < 0:
        return 0
    if i < len(arr):
        val = arr[i]
        while n < len(arr) and eq(arr[n], val):
            n += 1
        return n
    return len(arr)

def collapse_index(lst, index):
    info = []
    i = 0
    while i < len(lst):
        curr = list(lst[i][:index]) + [[lst[i][index]]] + list(lst[i][index + 1:])
        c1 = list(lst[i][:index]) + list(lst[i][index + 1:])
        i += 1
        while i < len(lst) and list(lst[i][:index]) + list(lst[i][index + 1:]) == c1:
            curr[index].append(lst[i][index])
            i += 1
        info.append(curr)
        #print(curr)
    return info

def get_filename(base, ext):
    n = 0
    mid = ''
    name = ''
    while True:
        try:
            name = base + mid + ext
            file = open(name, 'r')
            file.close()
            n += 1
            mid = '-' + str(n)
        except:
            break
    return name

def most_least_populous(conn,c):
    # while True:
    #     try:
    #         int_N = int(input("Enter number of locations: "))
    #     except Exception as e:
    #         print("Invalid input. Please try again")
    #         continue
    #     break
        
    int_N = int(input("Enter number of locations: "))

    # query to find the most/least populous areas 
    c.execute(''' SELECT 
                p.Neighbourhood_Name as name, Latitude as lat, Longitude as long,CANADIAN_CITIZEN+NON_CANADIAN_CITIZEN+NO_RESPONSE as total_pop
                FROM population p, coordinates c
                WHERE p.Neighbourhood_Name = c.Neighbourhood_Name
                GROUP BY p.Neighbourhood_Name, total_pop
                HAVING total_pop > 0
                ORDER BY total_pop DESC''')
    areas = c.fetchall()
    areas = list(areas)
    num_areas = len(areas)

    # list 'most_populous' contains the top N most populous areas, including ties
    most_populous = []
    i = 0                   # index to list most_populous,helps in cases with tie
    j = 0                   # counter for the number of locations entered 
    prev = None
    
    while j < int_N and i < num_areas:
        most_populous.append(areas[i][3])
        if areas[i][3] != prev and len(most_populous) <= int_N:
            prev = areas[i][3]
            j += 1
        i += 1
    
    # list 'least_populous' contains the top N most populous areas, including ties
    areas_rev = areas.copy()
    areas_rev.reverse()
    least_populous = []
    i = 0                   # index to list most_populous,helps in cases with tie
    j = 0                   # counter for the number of locations entered 
    prev = None
    while j < int_N and i < num_areas:
        least_populous.append(areas_rev[i][3])
        if areas_rev[i][3] != prev and len(least_populous) <= int_N:
            prev = areas_rev[i][3]
            j += 1
        i += 1
    
    # popul_sum is used to scale the siz of the circle markers
    popul_sum = sum(most_populous) + sum(least_populous)

    # self note: check the bounds of location
    m = folium.Map(location = [53.5444,-113.323],zoom_start=11)

    # map the most populous areas
    for index in range(len(most_populous)):
        folium.Circle(
            location = [areas[index][1], areas[index][2]],
            popup = areas[index][0] + "<br>" + str(areas[index][3]),
            # self note: NEED TO ADJUST THE RADIUS 
            radius = (areas[index][3]/popul_sum)*5000,
            color = 'crimson',
            fill = True,
            fill_color = 'crimson').add_to(m)
            # self note: ADD COUTNER , CHECK ASSIGNMENT SPEC 
        m.save("Q2.html")
    # map the least populous areas
    for index in range(len(least_populous)):
        folium.Circle(
            location = [areas_rev[index][1], areas_rev[index][2]],
            popup = areas_rev[index][0] + "<br>" + str(areas_rev[index][3]),
            # self note: NEED TO ADJUST THE RADIUS 
            radius = (areas_rev[index][3]/popul_sum)*5000,
            color = 'crimson',
            fill = True,
            fill_color = 'crimson').add_to(m)
            # self note: ADD COUTNER , CHECK ASSIGNMENT SPEC 
        m.save("Q2.html")
    
    # conn.commit()
    return

def n_highest_crime_population_ratios(conn, c):
    lb, ub = get_range_years()
    n = 0
    while True:
        try:
            n = int(input("Enter the number of locations: "))
            assert(n > 0)
        except:
            print("Invalid input, please try again. ")
            continue
        break

    query = '''
    select P.n_name, (C.total_crimes*1.0) / P.total_pop as crime_ratio, M.mcc, L.Latitude, L.Longitude
    from
        (select Neighbourhood_Name as n_name, CANADIAN_CITIZEN + NON_CANADIAN_CITIZEN + NO_RESPONSE as total_pop
        from population
        where total_pop > 0) as P,
        (select Neighbourhood_Name as n_name, sum(Incidents_Count) as total_crimes
        from crime_incidents
        where Year >= {} and Year <= {}
        group by n_name) as C,
        (select n_name, mcc
        from (select Neighbourhood_Name as n_name, Crime_Type as mcc, count(*) as cnt 
             from crime_incidents
             where Year >= {} and Year <= {}
             group by n_name, mcc) as CTS,
             (select n_name1, max(cnt) as mx
             from (select Neighbourhood_Name as n_name1, Crime_Type as mcc, count(*) as cnt 
                  from crime_incidents
                  where Year >= {} and Year <= {}
                  group by n_name1, mcc)
             group by n_name1) as MXS
        where CTS.n_name = MXS.n_name1 and CTS.cnt = MXS.mx) as M,
        (select Neighbourhood_name as n_name, Latitude, Longitude
        from coordinates
        where Latitude != 0.0 and Longitude != 0.0) as L
    where P.n_name = C.n_name and C.n_name = M.n_name and M.n_name = L.n_name
    order by crime_ratio desc;
    '''.format(lb, ub, lb, ub, lb, ub)

    info = collapse_index(list(c.execute(query).fetchall()), 2)
    info = info[:first_n_with_ties(info, (lambda l1, l2: l1[1] == l2[1]), n)]

    m = folium.Map(location = [53.5444, -113.323], zoom_start = 11)

    for i in info:
        folium.Circle(
            location = [i[3], i[4]],
            popup = "{} <br> {} <br> {}".format(i[0], ", ".join(i[2]), i[1]),
            radius= 1000*i[1],
            color= 'crimson',
            fill= True,
            fill_color= 'crimson'
        ).add_to(m)

    m.save(get_filename("Q4", ".html"))

def main():
    #'''
    while True:
        try:
            conn, c = connect(input("Enter the name of the database: "))
        except:
            print("Incorrect input. Please try again.")
            continue
        break
    #'''
    #conn, c = connect("./a4-sampled.db")
    
    functions = [most_least_populous, n_highest_crime_population_ratios]
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
    # conn.commit()
    # conn.close()

main()
