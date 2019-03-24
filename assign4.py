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
def main():
    while True:
        try:
            conn, c = connect(input("Enter the name of the database: "))
        except:
            print("Incorrect input. Please try again.")
            continue
        break
    
    functions = [most_least_populous]
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