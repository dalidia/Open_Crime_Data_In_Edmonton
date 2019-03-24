import sqlite3
import pandas as pd
import numpy as np
import folium

def most_least_populous(conn,c):
    while True:
        try:
            int_N = int(input("Input an integer: "))
        except Exception as e:
            print("Invalid input. Please try again")
            continue
        break
        
    # int_N = int(input("Input an integer: "))

    # query to find the most/least populous areas 
    c.excecute(''' SELECT 
                p.Neighbourhood_Name as name, Latitude as lat, Longitude as long,CANADIAN_CITIZEN+NON_CANADIAN_CITIZEN+NO_RESPONSE as total_pop
                FROM population p, coordinates c
                WHERE p.Neighbourhood_Name = c.Neighbourhood_Name
                GROUP BY p.Neighbourhood_Name, total_pop
                ORDER BY total_pop DESC''')
    areas = c.fetchall()
    areas = list(areas)
    print(areas[1])

    # plotting N most populous areas using folium


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