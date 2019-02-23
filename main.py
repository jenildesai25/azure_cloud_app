import csv
import os
import hashlib
import random
import time
from flask import Flask, render_template, request
from db import Database, RedisCache
from datetime import datetime
from json import loads, dumps

app = Flask(__name__, template_folder='templates')

# Connect to db
# database = Database()
# redis = RedisCache().connection


@app.route('/')
def hello_world():
    return 'Hello, World!'

    # return render_template('index.html', earthquakes=[])


@app.route('/analyze_randomq')
def analyze_randomq():
    cnt = int(request.args.get('count', 0))
    source = request.args.get('source', 'sqldb')
    random_list = [round(random.uniform(0, 10), 2) for i in range(cnt)]

    columns = ['time', 'latitude', 'longitude', 'place', 'mag']
    columns_str = '"' + '","'.join(columns) + '"'

    sqlquery = 'select {columns_str} from dbo.all_month where mag={mag};'
    cursor = database.connection.cursor()
    t = time.time()
    if source == 'cache':
        source_used = 'Redis Cache'
        for mag in random_list:
            formatted_query = sqlquery.format(columns_str=columns_str, mag=mag)
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

                result = loads(redis.get(query_hash)).decode()
    else:
        source_used = 'Azure SQL'
        for mag in random_list:
            formatted_query = sqlquery.format(columns_str=columns_str, mag=mag)
            query_hash = hashlib.sha256(formatted_query.encode()).hexdigest()
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

    return render_template('results.html', time_taken=time_taken, count=cnt, source=source_used)


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


@app.route('/upload_data', methods=['POST'])
def upload():
    sqlquery = 'Insert into "all_month" ({columns}) values ({values})'
    tempfile = request.files['files']
    filename = 'tempcsv'
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


if __name__ == '__main__':
    app.run(debug=True)
