from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def index():
    ## sqlite3 
    return render_template('home.html')

@app.route("/home")
def home():
    return render_template("home.html", valid=False)

@app.route("/question1")
def question1():
    return render_template("question1.html")

@app.route("/question1", methods=['POST', 'GET'])
def question1_interface():
    lb = request.form['lb']
    up = request.form['up']
    crime_index = request.form['crime_index']

    try:
		lb = int(lb)
		up = int(up)
	except:
		return "<>"
	else:
		if lb <= up:
			break
		print("Upper bound is less than lower bound. Please enter bounds again.")
    pass

@app.route("/question2")
def question2():
    return render_template("question2.html")

@app.route("/question3")
def question3():
    return render_template("question3.html")

@app.route("/question4")
def question4():
    return render_template("question4.html")

if __name__ == '__main__':
    app.run(debug=True)