import mysql.connector
db_conn = mysql.connector.connect(host="localhost", user="root",
password="Password", database="events")
db_cursor = db_conn.cursor()


db_cursor.execute('''
          DROP TABLE employees;
          ''')


db_cursor.execute('''
          DROP TABLE request_leave;
          ''')


db_conn.commit()
db_conn.close()