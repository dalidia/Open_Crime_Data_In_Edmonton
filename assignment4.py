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

def get_range(conn,c):
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
	lb, up = get_range(conn,c)
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
	lb, up = get_range(conn,c)
	crime_type = get_crime_type(conn,c,)

	param = (lb,up, crime_type)
	c.execute('''SELECT c.Neighbourhood_Name, d.Latitude, d.Longitude, sum(Incidents_Count)  as g
		FROM crime_incidents c, coordinates d
		WHERE c.Year >= ? and c.Year <= ? and c.Crime_Type= ?  and c.Neighbourhood_Name = d.Neighbourhood_Name
		group by c.Neighbourhood_Name, d.Latitude, d.Longitude 
		order by g desc''', param)
	neigh_name= c.fetchall()
	neigh_name = list(neigh_name)
	num_neigh = len(neigh_name)

	while True:
		try:
			int_N = int(input("Enter number of locations: "))
		except Exception as e:
			print("Invalid input. Please try again")
			continue
		break
  # list 'most_incidents contains the top N neighbourhoods, including ties
	most_incidents = []
	i = 0                   # index to list most_populous,helps in cases with tie
	j = 0                   # counter for the number of locations entered 
	prev = None

	while j < int_N and i < num_neigh:
		most_incidents.append(neigh_name[i][3])
		if neigh_name[i][3] != prev and len(most_incidents) <= int_N:
			prev = neigh_name[i][3]
			j += 1
		i += 1
	m = folium.Map(location = [53.5444,-113.323],zoom_start=11)
	# incident_sum = sum(neigh_name)
	for index in range(len(most_incidents)):
		folium.Circle(
			location = [neigh_name[index][1], neigh_name[index][2]],
			popup = neigh_name[index][0] + "<br>" + str(neigh_name[index][3]),
			# self note: NEED TO ADJUST THE RADIUS 
			radius = 100,
			color = 'crimson',
			fill = True,
			fill_color = 'crimson').add_to(m)
      # self note: ADD COUTNER , CHECK ASSIGNMENT SPEC 
		m.save("Q3.html")
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

	functions = [show_barplot_range, function_3]
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
