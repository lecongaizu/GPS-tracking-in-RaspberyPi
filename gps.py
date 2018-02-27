from flask import Flask
from flask import render_template
from flask import request
import serial
import pynmea2
import datetime
import collections
import json
import time 
import sqlite3 as sql
app = Flask(__name__)


@app.route('/', methods = ['POST', 'GET'])
def index():
	gps = serial.Serial("/dev/serial0", 9600, timeout= 0.5)
	while True:
		line = gps.readline()
		data = line.split(",".encode())
		if data[0] == "$GPRMC".encode():
			if data[2] == "A".encode():
				
				localtime = time.localtime(time.time())
				datetime = str(localtime[0])+"-"+str(localtime[1])+"-"+str(localtime[2])+" "+str(localtime[3])+":"+str(localtime[4])+":"+str(localtime[5])
				
				latgps = float(data[3].decode())
				if data[4] == "S".encode():
					latgps = -latgps
				latdeg = int(latgps/100)
				latmin = latgps - latdeg*100
				lat = round((latdeg+(latmin/60)),6)
				
				longps = float(data[5].decode())
				if data[6] == "W".encode():
					longps = -longps
				longdeg = int(longps/100)
				longmin = longps - longdeg*100
				lon = round((longdeg + (longmin/60)),6)
				
				with sql.connect("databasegps.db") as con:
					cur = con.cursor()
					cur.execute("INSERT INTO gps (times,latitudes, longitudes) VALUES (?,?,?)", (datetime,lat, lon))
					con.commit()
					con = sql.connect("databasegps.db")
					con.row_factory = sql.Row
					cur = con.cursor()
					cur.execute("select * from gps")
					rows = cur.fetchall();
					object_list = []
					json_data = {"id":1}
					
					for row in rows:
						d = collections.OrderedDict()
						d['date_time'] = row["times"]
						d['latitude'] = row["latitudes"]
						d['longitude'] = row["longitudes"]
						object_list.append(d)
						
					json_data["gps_data"] = object_list
					json_gps = json.dumps(json_data, indent = 4)
					object_file = 'gpsdata.js'
					with open(object_file,'w') as pos:
						pos.write("%s\n" %(json_gps))
				return render_template('main.html',time = time,lat= lat ,lon = lon, rows = rows)										

if __name__ == '__main__':
   app.run(debug = True)


