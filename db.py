import pypyodbc
# from credentials import SQL_DB, REDIS_DB
from redis import StrictRedis

# import mysql.connector
# from credentials import MYSQL_DB

# SQL_DB = {
#     "Driver": "{ODBC Driver 13 for SQL Server}",
#     "Server": "tcp:cse6331sqlserver.database.windows.net,1433",
#     "Database": "cloudsqldb",
#     "Uid": "jenildesai25",
#     "Pwd": "Bhavya@1008",
#     "Encrypt": "yes",
#     "TrustServerCertificate": "no",
#     "Connection Timeout": 30
# }

SQL_DB = {
    "Driver": "{ODBC Driver 13 for SQL Server}",
    "Server": "tcp:cse6331sqlserver.database.windows.net,1433",
    "Database": "cloudsqldb",
    "Uid": "jenildesai25@cse6331sqlserver",
    "Pwd": "Bhavya@1008",
    "Encrypt": "yes",
    "TrustServerCertificate": "yes",
    "Connection Timeout": 30
}
# MYSQL_DB = {
#     'host': 'azmysqldb.mysql.database.azure.com',
#     'user': 'chaitanya@azmysqldb',
#     'password': 'Cl0uduta',
#     'database': 'azmysqldb'
# }
REDIS_DB = {
    'host': 'cse6331azureredis.redis.cache.windows.net',
    'port': 6380,
    'db': 0,
    'password': 'nLqjAKLdORnQot4eWD3PAOGOoW0GGsJFOSgICutxIlg=',
    'ssl': True
}
# cse6331azureredis.redis.cache.windows.net:6380,password=nLqjAKLdORnQot4eWD3PAOGOoW0GGsJFOSgICutxIlg=,ssl=True,
azure_login = [
    {
        "cloudName": "AzureCloud",
        "id": "17620b2e-e729-445f-af8a-89e0344738d9",
        "isDefault": True,
        "name": "Azure for Students",
        "state": "Enabled",
        "tenantId": "5cdc5b43-d7be-4caa-8173-729e3b0a62d9",
        "user": {
            "name": "jenilbimal.desai@mavs.uta.edu",
            "type": "user"
        }
    }
]


class Database(object):

    def __init__(self):
        try:
            self.connection = pypyodbc.connect('DRIVER={Driver};SERVER={Server};PORT=1443;DATABASE={Database};UID={Uid};PWD={Pwd}'.format(**SQL_DB))

        except Exception as e:
            print(e)


class RedisCache(object):

    def __init__(self):
        try:
            self.connection = StrictRedis(**REDIS_DB)
        except Exception as e:
            print(e)
