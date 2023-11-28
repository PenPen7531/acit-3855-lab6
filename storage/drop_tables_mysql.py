import mysql.connector
db_conn = mysql.connector.connect(host="acit-3855-kakfa-jwang.eastus.cloudapp.azure.com", user="root",
password="Password", database="events")
db_cursor = db_conn.cursor()


db_cursor.execute('''
          DROP TABLE Employees;
          ''')


db_cursor.execute('''
          DROP TABLE Request_Leave;
          ''')


db_conn.commit()
db_conn.close()