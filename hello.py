
from flask import Flask, render_template,request 
from datetime import date, timedelta
import pyodbc
import math  
import pandas as pd
import numpy as np
import json

app = Flask(__name__, static_url_path='')

cnxn = pyodbc.connect('''Driver={ODBC Driver 17 for SQL Server};
                        Server=tcp:adbmic.database.windows.net,1433;
                        Database=adb1;
                        Uid=server1;
                        Pwd=Sniffy@25;
                        Encrypt=yes;
                        TrustServerCertificate=no;
                        Connection Timeout=30;''')


@app.route('/')
def root():
    return render_template('index.html')

def getDistance(lat_1,lon_1,lat_2,lon_2):
    radius = 6371
    distance_lat = np.deg2rad(lat_2-lat_1)
    distance_lon = np.deg2rad(lon_2-lon_1)
    a = math.sin(distance_lat/2) * math.sin(distance_lat/2) +  math.cos(np.deg2rad(lat_1)) * math.cos(np.deg2rad(lat_2)) * math.sin(distance_lon/2) * math.sin(distance_lon/2) 
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)); 
    distance = radius * c
    return distance

@app.route('/searchAreainkm', methods=['POST'])
def searchAreainkm():
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])
    km = float(request.form['distance'])

    selectQuery = 'select * from all_month'
    cursor = cnxn.cursor()
    rows = cursor.execute(selectQuery)

    count = 0
    for row in rows:
        latit3=float(row[1])
        longi3=float(row[2])
        distance=getDistance(latitude,longitude,latit3,longi3)
        if distance<=km:
            count = count + 1
    cursor.close()
    return render_template('searchAreainkm.html', count = count, distance=km)

@app.route('/magnitude5', methods=['POST'])
def magnitude5():
    magnitude = float(request.form['magnitude5'])
    selectQuery = 'select * from all_month where mag >= ?'
    cursor = cnxn.cursor()
    rows = cursor.execute(selectQuery,magnitude)
    count = 0
    for row in rows:
        count = count + 1
    
    return render_template('magnitude5.html', count = count, magnitude=magnitude, rows = rows)

@app.route('/daynight', methods=['POST'])
def daynight():
    selectQuery = 'select * from all_month where (Times_hh > 20 or Times_hh < 5) and mag > 4'
    cursor = cnxn.cursor()
    rows = cursor.execute(selectQuery)
    count = 0
    for row in rows:
        count = count + 1

    selectQuery = 'select * from all_month where (Times_hh < 20 or Times_hh > 5) and mag > 4'
    cursor = cnxn.cursor()
    rows = cursor.execute(selectQuery)
    day = 0
    for row in rows:
        day = day + 1
    
    return render_template('daynight.html', count = count, day=day)



@app.route('/rangemagnitude', methods=['POST'])
def rangemagnitude():
    days = float(request.form['days'])
    Min_magnitude = float(request.form['Min_magnitude'])
    Max_magnitude = float(request.form['Max_magnitude'])
    
    endDate = str(date.today() - timedelta(days))
    cursor = cnxn.cursor()
    rows = []
    rows = cursor.execute('select * from all_month where mag in (?,?) and time >= ?' , Min_magnitude,Max_magnitude,endDate)
    count = 0
    for row in rows:
        count = count + 1 
  
    return render_template('rangemagnitude.html',count=count,Min_magnitude=Min_magnitude,Max_magnitude=Max_magnitude,days=endDate) 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)