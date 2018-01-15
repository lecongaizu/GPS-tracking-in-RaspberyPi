from flask import Flask
from flask import render_template
from flask import request
import serial
import pynmea2
import datetime
import time 
import sqlite3 as sql
import arrow
app = Flask(__name__)


@app.route('/', methods = ['POST', 'GET'])
def index():
	gps = serial.Serial("/dev/serial0", 9600, timeout= 0.5)
	while True:
		line = gps.readline()
		data = line.split(",")
		if data[0] == "$GPRMC":
			if data[2] == "A":
				time = datetime.datetime.now() 
				lat = data[3]
				lon = data[5]
				with sql.connect("database.db") as con:
					cur = con.cursor()
					cur.execute("INSERT INTO gps (times,latitudes, longitudes) VALUES (?,?,?)", (time,lat, lon))
					con.commit()
					con = sql.connect("database.db")
					con.row_factory = sql.Row
					cur = con.cursor()
					cur.execute("select * from gps")
					rows = cur.fetchall();
				return render_template('main.html',time = time,lat= lat ,lon = lon, rows = rows)										

if __name__ == '__main__':
   app.run(debug = True)


