# Jenil Desai - 0245
# CSE-6331
# Assignment4

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
    s_mag = float(request.args.get('smag', 2))
    e_mag = float(request.args.get('emag', 3))
    cnt = int(request.args.get('count', 0))
    # age = int(request.args.get('age', 10))
    source = request.args.get('source', 'sqldb')
    random_list = [round(random.uniform(s_mag, e_mag), 1) for i in range(cnt)]
    columns = ['time', 'latitude', 'longitude', 'place', 'mag']
    columns_str = '"' + '","'.join(columns) + '"'

    sqlquery = 'select {columns_str} from dbo.all_month where mag={mag};'
    cursor = database.connection.cursor()
    t = time.time()
    time_of_1st = 0
    total_time_taken = 0
    result_1st = []
    new_data = []
    if source == 'cache':
        source_used = 'Redis Cache'
        for mag in random_list:
            formatted_query = sqlquery.format(columns_str=columns_str, mag=mag)
            query_hash = hashlib.sha256(formatted_query.encode()).hexdigest()
            t = time.time()

            result = redis.get(query_hash)
            if result:
                result = loads(result.decode())
            else:
                cursor.execute(formatted_query)
                rows = cursor.fetchall()

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
            total_time_taken += (time.time() - t)
            # if time_of_1st == 0:
            # time_of_1st = deepcopy(total_time_taken)
            result_1st = result
            # new_data = []
            # for i, value in enumerate(result_1st):
            #     new_data.append([result_1st[i]['latitude'], result_1st[i]['longitude']])

    else:
        source_used = 'Azure SQL'
        for mag in random_list:
            formatted_query = sqlquery.format(columns_str=columns_str, mag=mag)
            query_hash = hashlib.sha256(formatted_query.encode()).hexdigest()
            t = time.time()

            cursor.execute(formatted_query)

            total_time_taken += (time.time() - t)

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
            result_1st = result

            # new_data = []
            # for i, value in enumerate(result_1st):
            #     new_data.append([result_1st[i]['latitude'], result_1st[i]['longitude']])
            # if time_of_1st == 0:
            #     time_of_1st = deepcopy(total_time_taken)
            #     result_1st = result

    return render_template('results.html', time_taken=total_time_taken, count=cnt, source=source_used, earthquakes=result_1st)


@app.route('/analyze_sameq')
def analyze_sameq():
    year = int(request.args.get('year', 2017))
    range1 = int(request.args.get('range1', 20))
    range1end = int(request.args.get('range1end', 50))
    # range2 = int(request.args.get('range2', 10))
    # range2end = int(request.args.get('range2end', 20))
    # range3 = int(request.args.get('range3', 0))
    # range3end = int(request.args.get('range3end', 10))
    # year_start = int(request.args.get('yearstart', 2010))
    # year_end = int(request.args.get('yearend', 2018))
    source = request.args.get('source', 'sqldb')
    # random_list = [round(random.uniform(s_mag, e_mag), 1) for i in range(cnt)]
    # columns = ['time', 'latitude', 'longitude', 'place', 'mag']
    # columns_str = '"' + '","'.join(columns) + '"'
    years = []

    years.append((range1, range1end))
    # years.append((range2, range2end))
    # years.append((range3, range3end))
    # for i in range(year_start, year_end + 1):
    #     years.append(i)
    formatted_data = []
    # sqlquery = 'select * from dbo.minnow;'
    cursor = database.connection.cursor()
    t = time.time()
    time_of_1st = 0
    total_time_taken = 0
    result_1st = []
    new_data = []
    if source == 'cache':
        source_used = 'Redis Cache'
        while range1 <= range1end:
            sqlquery = 'select count(*) as counts from population where [{}] between {} and {};'.format(year, range1, range1end)
            formatted_query = sqlquery
            query_hash = hashlib.sha256(formatted_query.encode()).hexdigest()
            t = time.time()

            result = redis.get(query_hash)
            if result:
                result = loads(result.decode())
            else:
                cursor.execute(formatted_query)
                rows = cursor.fetchall()

                for row in rows:
                    quake = dict()
                    quake[year] = row['{}'.format(str(year))]
                    # for i, val in enumerate(row):
                    #     if type(val) == datetime:
                    #         val = time.mktime(val.timetuple())
                    #     # quake[columns[i]] = val
                    formatted_data.append(quake)
                redis.set(query_hash, dumps(formatted_data))

                result = redis.get(query_hash)
            result = loads(result.decode())
            total_time_taken += (time.time() - t)
            # if time_of_1st == 0:
            # time_of_1st = deepcopy(total_time_taken)
            result_1st = result
            # new_data = []
            # for i, value in enumerate(result_1st):
            #     new_data.append([result_1st[i]['latitude'], result_1st[i]['longitude']])

    else:
        source_used = 'Azure SQL'
        new_data = []
        # magStart = 0
        # magEnd = magStart + range1end

        while range1 < 1000000:
            print(range1)
            sqlquery = 'select count(*) as counts from population where [{}] between {} and {};'.format(year, range1, range1end)
            formatted_query = sqlquery
            query_hash = hashlib.sha256(formatted_query.encode()).hexdigest()
            t = time.time()
            cursor.execute(formatted_query)
            total_time_taken += (time.time() - t)

            rows = cursor.fetchall()
            # if rows:
            #     print('Values present for: ',query_hash)

            for row in rows:
                formatted_data.append({"# People": row['counts'], "Age Range": '{}'.format(range1) + " to " + '{}'.format(range1end)})
            #     quake['year'] = year
            #     quake['']
            #     # for i, val in enumerate(row):
            #     #     if type(val) == datetime:
            #     #         val = time.mktime(val.timetuple())
            #     # quake[columns[i]] = val
            #     formatted_data.append(quake)
            redis.set(query_hash, dumps(formatted_data))
            range1 = range1 + 300000
        result = formatted_data
        result_1st = result

        # new_data = []
        # for i, value in enumerate(result_1st):
        #     new_data.append([result_1st[i]['latitude'], result_1st[i]['longitude']])
        # if time_of_1st == 0:
        #     time_of_1st = deepcopy(total_time_taken)
        #     result_1st = result

    return render_template('results.html', time_taken=total_time_taken, count=0, source=source_used, earthquakes=result_1st)


@app.route('/analyze_bl')
def analyze_bl():
    code = request.args.get('code', 'CRI')
    start = int(request.args.get('start', 1980))
    end = int(request.args.get('end', 2010))
    cnt = 0
    # age = int(request.args.get('age', 10))
    source = request.args.get('source', 'sqldb')
    # random_list = [round(random.uniform(s_mag, e_mag), 1) for i in range(cnt)]
    # columns = ['time', 'latitude', 'longitude', 'place', 'mag']
    # columns_str = '"' + '","'.join(columns) + '"'
    random_list = []
    random_list.append((start, end))
    # while s_mag <= e_mag:
    #     temp = s_mag + 0.5
    #     random_list.append((s_mag, temp))
    #     s_mag = temp + 0.01

    sqlquery = 'select Year,BLPercent from dbo.educationshare where Code like \'%{}%\' and Year between {} and {};'
    cursor = database.connection.cursor()
    t = time.time()
    time_of_1st = 0
    total_time_taken = 0
    result_1st = []
    new_data = []
    if source == 'cache':
        source_used = 'Redis Cache'
        for start, end in random_list:
            formatted_query = sqlquery.format(start, end)
            query_hash = hashlib.sha256(formatted_query.encode()).hexdigest()
            t = time.time()

            result = redis.get(query_hash)
            if result:
                result = loads(result.decode())
            else:
                cursor.execute(formatted_query)
                rows = cursor.fetchall()

                formatted_data = []
                for row in rows:
                    formatted_data.append({"count": str(row['counts']), "year": str(row['year'])})
                redis.set(query_hash, dumps(formatted_data))

                result = redis.get(query_hash)
            result = loads(result.decode())
            total_time_taken += (time.time() - t)
            # if time_of_1st == 0:
            # time_of_1st = deepcopy(total_time_taken)
            result_1st = result
            # new_data = []
            # for i, value in enumerate(result_1st):
            #     new_data.append([result_1st[i]['latitude'], result_1st[i]['longitude']])

    else:
        source_used = 'Azure SQL'
        for start, end in random_list:
            formatted_query = sqlquery.format(code, start, end)
            query_hash = hashlib.sha256(formatted_query.encode()).hexdigest()
            t = time.time()

            cursor.execute(formatted_query)

            total_time_taken += (time.time() - t)

            rows = cursor.fetchall()

            # if rows:
            #     print('Values present for: ',query_hash)
            formatted_data = []
            for i, row in enumerate(rows):
                formatted_data.append({"year": str(row['year']), "blpercent": str(row['blpercent'])})
            redis.set(query_hash, dumps(formatted_data))

            result = formatted_data
            result_1st = result

            # new_data = []
            # for i, value in enumerate(result_1st):
            #     new_data.append([result_1st[i]['latitude'], result_1st[i]['longitude']])
            # if time_of_1st == 0:
            #     time_of_1st = deepcopy(total_time_taken)
            #     result_1st = result

    return render_template('result.html', time_taken=total_time_taken, count=cnt, source=source_used, earthquakes=result_1st)


# @app.route('/get_some')
# def get_some():
#     columns = ['time', 'latitude', 'longitude', 'place', 'mag']
#     sqlquery = 'select top 10 {columns} from dbo.all_month;'.format(columns='"' + '","'.join(columns) + '"')
#     cursor = database.connection.cursor()
#     cursor.execute(sqlquery)
#     row = cursor.fetchone()
#     all_data = []
#
#     while row:
#         quake = dict()
#         for i, val in enumerate(row):
#             quake[columns[i]] = val
#         all_data.append(quake)
#         row = cursor.fetchone()
#     print('QUAKEs:', all_data)
#     return render_template('index.html', earthquakes=all_data)
#
#
# @app.route('/createtable')
# def createTable():
#     try:
#         lstDictionaryData = []
#         # conn = pypyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1443;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
#         cursor = database.connection.cursor()
#         # query = "drop table dbo.people"
#         # cursor.execdirect(query)
#         # query = "CREATE TABLE dbo.all_month (\"time\" datetime, \"latitude\" FLOAT, \"longitude\" FLOAT, \"depth\" FLOAT, \"mag\" FLOAT, \"magType\" TEXT, \"nst\" INT, \"gap\" INT, \"dmin\" FLOAT, \"rms\" FLOAT, \"net\" TEXT, \"id\" TEXT, \"updated\" datetime, \"place\" TEXT, \"type\" TEXT, \"horontalError\" FLOAT, \"depthError\" FLOAT, \"magError\" FLOAT, \"magNst\" INT, \"status\" TEXT, \"locationSource\" TEXT, \"magSource\" TEXT)"
#         # query = "CREATE TABLE dbo.all_month(time DATETIME,latitude FLOAT,longitude FLOAT,depth FLOAT,mag FLOAT,magType TEXT,nst INT,gap INT,dmin FLOAT,rms FLOAT,net TEXT,id TEXT,updated DATETIME,place TEXT,type TEXT,horontalError FLOAT,depthError FLOAT,magError FLOAT,magNst INT,status TEXT,locationSource TEXT,magSource TEXT)"
#         query = "CREATE TABLE dbo.people(Name TEXT, Grade INT, Room INT, Telnum INT, Picture TEXT, Keywords TEXT)"
#         startTime = time.time()
#         # cursor.execute(query)
#         cursor.execdirect(query)
#         # cursor.execdirect("CREATE INDEX all_month_mag__index ON cloudsqldb.dbo.earthquake (mag)")
#         # cursor.execdirect("CREATE INDEX all_month_lat__index ON cloudsqldb.dbo.earthquake (latitude)")
#         # cursor.execdirect("CREATE INDEX all_month_long__index ON cloudsqldb.dbo.earthquake (longitude)")
#         endTime = time.time()
#         # conn.close()
#         executionTime = (endTime - startTime) * 1000
#         return render_template('results.html', earthquakes=lstDictionaryData, count=lstDictionaryData.__len__(), time_taken=executionTime)
#     except Exception as e:
#         print(e)
#
#
# @app.route('/upload_data', methods=['POST'])
# def upload():
#     try:
#         createTable()
#         tempfile = request.files['file']
#         # sqlquery = 'Insert into "all_month" ({columns}) values ({values})'
#         sqlquery = 'Insert into dbo.people ({columns}) values ({values})'
#         filename = 'temp.csv'
#         tempfile.save(os.path.join(filename))
#
#         csv_file = open(filename, 'r')
#         reader = csv.DictReader(csv_file)
#         for row in reader:
#             cols = '"' + '","'.join(row.keys()) + '"'
#             vals = '\'' + '\',\''.join(row.values()) + '\''
#             q = sqlquery.format(columns=cols, values=vals)
#             print("QUERy:", q)
#             cursor = database.connection.cursor()
#             cursor.execute(q)
#             database.connection.commit()
#             print('commit executed.')
#         csv_file.close()
#         # file.save(os.path.join(Uploadpath, file_name))
#         # con = engine.connect()
#         # df = pd.read_csv(os.path.join(Uploadpath, file_name))
#         # tab_file = file_name.split('.')[0]
#         # start_time = time.time()
#         # df.to_sql(name=tab_file, con=con, if_exists='replace', index=False)
#         # end_time = time.time()
#         # diff = str((end_time - start_time) * 1000)
#         # con.close()
#         return render_template('index.html', earthquakes=[])
#     except Exception as e:
#         return render_template('index.html', earthquakes=[])


if __name__ == '__main__':
    app.run(debug=True)
