import folium
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# connects database 
def connect(path):
	conn = sqlite3.connect(path)
	c =conn.cursor()
	c.execute('PRAGMA foreign_keys=ON; ')
	conn.commit()
	return conn, c

def get_range_years(conn,c):
	while True:
		try:
			lb = int(input("Enter start year (YYYY): "))
			up = int(input("Enter end year (YYYY): "))
		except:
			print("Invalid bounds. Please try again")
		else:
			if lb <= up:
				break
			print("Lower bound is less than upper bound. Please enter bounds again.")
	return lb, up

def get_crime_type(conn,c):
	df = pd.read_sql_query("SELECT distinct Crime_Type FROM crime_incidents", conn)
	crimes = df.Crime_Type.to_string(index=False)
	print(crimes)

	while True:
		crime_type = input("Enter the crime type: ").capitalize()
		if crime_type == 'Q':
			return
		elif crime_type in crimes:
			break
		else:
			print("Crime could not be found. Invalid crime, try again or press 'q' to quit")
	return crime_type

# show the barplot for a range of years and a type of crime
def show_barplot_range(conn,c):
	lb, up = get_range_years(conn,c)
	crime_type = get_crime_type(conn,c)

	query = '''SELECT Month, COUNT(*) FROM crime_incidents WHERE Year >= ? and 
	Year <= ? and Crime_Type= ? group by Month'''
	df = pd.read_sql_query(query,conn, params=(lb,up,crime_type))
	# graph barplot
	plot = df.plot.bar(x="Month")
	plt.plot()
	plt.show()
	conn.commit()
	return

def function_3(conn, c):
	lb, up = get_range_years(conn,c)
	crime_type = get_crime_type(conn,c,)

	query = '''SELECT c.Neighbourhood_Name, d.Latitude, d.Longitude, sum(Incidents_Count)  as g
	FROM crime_incidents c, coordinates d
WHERE c.Year >= 2017 and c.Year <= 2017 and c.Crime_Type= "Break and Enter"  and c.Neighbourhood_Name = d.Neighbourhood_Name
group by c.Neighbourhood_Name, d.Latitude, d.Longitude 
order by g desc'''




def main():
	while True:
		try:
			conn, c = connect(input("Enter the name of the database: "))
		except:
			print("Incorrect input. Please try again.")
			continue
		break

	functions = [show_barplot_range]
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
	return
 
 
main()
