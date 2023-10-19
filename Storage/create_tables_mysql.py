import mysql.connector
db_conn = mysql.connector.connect(host="acit-3855-kakfa-jwang.eastus.cloudapp.azure.com", user="root",
password="Password", database="events")
db_cursor = db_conn.cursor()


db_cursor.execute('''
          CREATE TABLE Request_Leave
          (id INT NOT NULL AUTO_INCREMENT, 
           trace_id VARCHAR(250) NOT NULL,
           employee_id VARCHAR(250) NOT NULL,
           days_off INTEGER NOT NULL,
           date_created DateTime NOT NULL,
           start_date DATE NOT NULL,
           end_date DATE NOT NULL,
           hours INTEGER NOT NULL,
           reason VARCHAR(100) NOT NULL,
           CONSTRAINT request_leave_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE Employees
          (id INT NOT NULL AUTO_INCREMENT, 
           trace_id VARCHAR(250) NOT NULL,
           employee_id VARCHAR(250) NOT NULL,
           address VARCHAR(250) NOT NULL,
           birth_date DATE NOT NULL,
           date_created DateTime NOT NULL,
           first_name VARCHAR(50) NOT NULL,
           last_name VARCHAR(50) NOT NULL,
           manager_code INTEGER NOT NULL,
           phone_number BIGINT NOT NULL,
           position VARCHAR(50) NOT NULL,
           salary INTEGER NOT NULL,
           CONSTRAINT employees_pk PRIMARY KEY (id))
          ''')


# Saves changes and closes DB session
db_conn.commit()
db_conn.close()