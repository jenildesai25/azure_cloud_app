# Jenil Desai - 0245
# CSE-6331
# Assignment3

import csv
import os
import hashlib
import random
import time
from flask import Flask, render_template, request
from db import Database, RedisCache
from datetime import datetime
from json import loads, dumps
from copy import deepcopy

app = Flask(__name__, template_folder='templates')

# Connect to db
database = Database()
redis = RedisCache().connection


@app.route('/')
def hello_world():
    # return 'Hello, World!'

    return render_template('index.html', earthquakes=[])

@app.route('/analyze_randomq')
def analyze_randomq():
    cnt = request.args.get('count', '')
    year = int(request.args.get('year', 2018))
    source = request.args.get('source', 'sqldb')
    # random_list = [round(random.uniform(0, 10), 2) for i in range(cnt)]
    # columns = ['time', 'latitude', 'longitude', 'place', 'mag']
    # columns_str = '"' + '","'.join(columns) + '"'
    sqlquery = 'select population.[{0}] from  population LEFT JOIN dbo.statecode ON dbo.statecode.ID = dbo.population.ID where statecode.[Short name] like \'%{1}%\';'.format(year, cnt)
    cursor = database.connection.cursor()
    t = time.time()
    # time_of_1st = 0
    # total_time_taken = 0
    # result_1st = []
    if source == 'cache':
        source_used = 'Redis Cache'
        # for mag in random_list:
        formatted_query = sqlquery
        query_hash = hashlib.sha256(formatted_query.encode()).hexdigest()
        # t = time.time()
        result = redis.get(query_hash)
        print(result)
        if not result:
            cursor.execute(formatted_query)
            rows = cursor.fetchall()
            formatted_data = []
            for row in rows:
                # quake = dict()
                # for i, val in enumerate(row):
                #     if type(val) == datetime:
                #         val = time.mktime(val.timetuple())
                #     # quake[columns[i]] = val
                formatted_data.append(row[0])
            redis.set(query_hash, dumps(formatted_data))
            # result = loads(redis.get(query_hash)).decode()
        else:
            result = loads(result.decode())
            # total_time_taken += (time.time() - t)
            # if time_of_1st == 0:
            #     time_of_1st = deepcopy(total_time_taken)
            #     result_1st = result

    else:
        source_used = 'Azure SQL'
        # for mag in random_list:
        formatted_query = sqlquery
        query_hash = hashlib.sha256(formatted_query.encode()).hexdigest()
        cursor.execute(formatted_query)
        rows = cursor.fetchall()

        # if rows:
        #     print('Values present for: ',query_hash)
        formatted_data = []
        for row in rows:
            formatted_data.append(row[0])
            # quake = dict()
            # for i, val in enumerate(row):
            #     if type(val) == datetime:
            #         val = time.mktime(val.timetuple())
            #     # quake[columns[i]] = val
            # formatted_data.append(quake)
        redis.set(query_hash, dumps(formatted_data))

            result = formatted_data

    time_taken = time.time() - t
    return render_template('results.html', time_taken=time_taken, count=cnt, source=source_used, earthquakes=result)


@app.route('/analyze_sameq')
def analyze_sameq():
    cnt = int(request.args.get('count', 0))
    source = request.args.get('source', 'sqldb')
    s_mag = float(request.args.get('s_mag', 2))
    e_mag = float(request.args.get('e_mag', 3))

    columns = ['time', 'latitude', 'longitude', 'place', 'mag']
    columns_str = '"' + '","'.join(columns) + '"'

    sqlquery = 'select {columns_str} from dbo.all_month where mag between {s_mag} and {e_mag};'
    cursor = database.connection.cursor()
    t = time.time()
    if source == 'cache':
        source_used = 'Redis Cache'
        for i in range(cnt):
            formatted_query = sqlquery.format(columns_str=columns_str, s_mag=s_mag, e_mag=e_mag)
            query_hash = hashlib.sha256(formatted_query.encode()).hexdigest()
            result = redis.get(query_hash)
            if result:
                pass
            else:
                cursor.execute(formatted_query)
                rows = cursor.fetchall()

                # if rows:
                #     print('Values present for: ',query_hash)

                formatted_data = []
                for row in rows:
                    quake = dict()
                    for i, val in enumerate(row):
                        if type(val) == datetime:
                            val = time.mktime(val.timetuple())
                        quake[columns[i]] = val
                    formatted_data.append(quake)
                redis.set(query_hash, dumps(formatted_data))

                result = redis.get(query_hash)
            result = loads(result.decode())
    else:
        source_used = 'Azure SQL'
        for ri in range(cnt):
            formatted_query = sqlquery.format(columns_str=columns_str, s_mag=s_mag, e_mag=e_mag)
            query_hash = hashlib.sha256(formatted_query.encode()).hexdigest()
            # print('QUERY:',formatted_query)
            cursor.execute(formatted_query)
            rows = cursor.fetchall()

            # if rows:
            #     print('Values present for: ',query_hash)
            formatted_data = []
            for row in rows:
                quake = dict()
                for i, val in enumerate(row):
                    if type(val) == datetime:
                        val = time.mktime(val.timetuple())
                    quake[columns[i]] = val
                formatted_data.append(quake)
            redis.set(query_hash, dumps(formatted_data))

            result = formatted_data

    time_taken = time.time() - t
    print('okay')
    return render_template('results.html', time_taken=time_taken, count=cnt, source=source_used, earthquakes=result)


@app.route('/get_some')
def get_some():
    columns = ['time', 'latitude', 'longitude', 'place', 'mag']
    sqlquery = 'select top 10 {columns} from dbo.all_month;'.format(columns='"' + '","'.join(columns) + '"')
    cursor = database.connection.cursor()
    cursor.execute(sqlquery)
    row = cursor.fetchone()
    all_data = []

    while row:
        quake = dict()
        for i, val in enumerate(row):
            quake[columns[i]] = val
        all_data.append(quake)
        row = cursor.fetchone()
    print('QUAKEs:', all_data)
    return render_template('index.html', earthquakes=all_data)


@app.route('/createtable')
def createTable():
    try:
        lstDictionaryData = []
        # conn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1443;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = database.connection.cursor()
        # query = "drop table dbo.people"
        # cursor.execdirect(query)
        # query = "CREATE TABLE dbo.all_month (\"time\" datetime, \"latitude\" FLOAT, \"longitude\" FLOAT, \"depth\" FLOAT, \"mag\" FLOAT, \"magType\" TEXT, \"nst\" INT, \"gap\" INT, \"dmin\" FLOAT, \"rms\" FLOAT, \"net\" TEXT, \"id\" TEXT, \"updated\" datetime, \"place\" TEXT, \"type\" TEXT, \"horontalError\" FLOAT, \"depthError\" FLOAT, \"magError\" FLOAT, \"magNst\" INT, \"status\" TEXT, \"locationSource\" TEXT, \"magSource\" TEXT)"
        # query = "CREATE TABLE dbo.all_month(time DATETIME,latitude FLOAT,longitude FLOAT,depth FLOAT,mag FLOAT,magType TEXT,nst INT,gap INT,dmin FLOAT,rms FLOAT,net TEXT,id TEXT,updated DATETIME,place TEXT,type TEXT,horontalError FLOAT,depthError FLOAT,magError FLOAT,magNst INT,status TEXT,locationSource TEXT,magSource TEXT)"
        query = "CREATE TABLE dbo.people(Name TEXT, Grade INT, Room INT, Telnum INT, Picture TEXT, Keywords TEXT)"
        startTime = time.time()
        # cursor.execute(query)
        cursor.execdirect(query)
        # cursor.execdirect("CREATE INDEX all_month_mag__index ON cloudsqldb.dbo.earthquake (mag)")
        # cursor.execdirect("CREATE INDEX all_month_lat__index ON cloudsqldb.dbo.earthquake (latitude)")
        # cursor.execdirect("CREATE INDEX all_month_long__index ON cloudsqldb.dbo.earthquake (longitude)")
        endTime = time.time()
        # conn.close()
        executionTime = (endTime - startTime) * 1000
        return render_template('results.html', earthquakes=lstDictionaryData, count=lstDictionaryData.__len__(), time_taken=executionTime)
    except Exception as e:
        print(e)


@app.route('/upload_data', methods=['POST'])
def upload():
    try:
        createTable()
        tempfile = request.files['file']
        # sqlquery = 'Insert into "all_month" ({columns}) values ({values})'
        sqlquery = 'Insert into dbo.people ({columns}) values ({values})'
        filename = 'temp.csv'
        tempfile.save(os.path.join(filename))

        csv_file = open(filename, 'r')
        reader = csv.DictReader(csv_file)
        for row in reader:
            cols = '"' + '","'.join(row.keys()) + '"'
            vals = '\'' + '\',\''.join(row.values()) + '\''
            q = sqlquery.format(columns=cols, values=vals)
            print("QUERy:", q)
            cursor = database.connection.cursor()
            cursor.execute(q)
            database.connection.commit()
            print('commit executed.')
        csv_file.close()
        # file.save(os.path.join(Uploadpath, file_name))
        # con = engine.connect()
        # df = pd.read_csv(os.path.join(Uploadpath, file_name))
        # tab_file = file_name.split('.')[0]
        # start_time = time.time()
        # df.to_sql(name=tab_file, con=con, if_exists='replace', index=False)
        # end_time = time.time()
        # diff = str((end_time - start_time) * 1000)
        # con.close()
        return render_template('index.html', earthquakes=[])
    except Exception as e:
        return render_template('index.html', earthquakes=[])


if __name__ == '__main__':
    app.run(debug=True)
