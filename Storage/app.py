# Jeffrey Wang
# Lab 3 - Storage file

import connexion
from connexion import NoContent
from base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from employee import Employee
from request_leave import RequestLeave
import datetime
import mysql.connector
import pymysql
import yaml
import logging
import logging.config






# Constants and DB configuration
PORT = 8090

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)




with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def log_data(event_name, table, trace_id):
    logger.debug(f"Stored event {event_name} request in {table} table with a trace id of {trace_id}")


def add_employee(body):
    "Converts and stores the new employee information into the Employees DB table. Information provided from the port 8080 server by API request"

    # Opens the DB session
    session = DB_SESSION()

    # Creates the SQL entry from python information
    emp = Employee(
        body['trace_id'],
        body['employee_id'],
        body['address'],
        body['birth_date'],
        body['first_name'],
        body['last_name'],
        body['manager_code'],
        body['phone_number'],
        body['position'],
        body['salary']
    )
   
    # Adds entry to the table
    session.add(emp)

    # Commits changes and closes DB session
    session.commit()
    session.close()

    log_data('Add Employee', 'employees', body['trace_id'])

    # Return 201 success
    return NoContent, 201

def request_time(body):
    "Stores the leave request information into the Request_Leave DB Table. Information provided from port 8080 server by API request"
    # Opens the database

    
    session = DB_SESSION()

    # Creates the SQL entry from python information
    lr = RequestLeave(  body['trace_id'],
                        body['employee_id'],
                        body['days_off'],
                        body['start_date'],
                        body['end_date'],
                        body['hours_off'],
                        body['reason'])


    # Adds entry to table
    session.add(lr)

    # Commits changes and closes DB session
    session.commit()
    session.close()

    log_data('Request Leave', 'request_leave', body['trace_id'])

    # Return 201 success
    return NoContent, 201


def get_employees(timestamp):
    "Gets employees from a specific timestamp"



    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    readings = session.query(Employee).filter(Employee.date_created >= timestamp_datetime)
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info("Query for Employees readings after %s returns %d results" %(timestamp, len(results_list)))
    return results_list, 200

    

def get_requests(timestamp):
    "Gets time off reqeusts from a specific timestamp"
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    readings = session.query(RequestLeave).filter(RequestLeave.date_created >= timestamp_datetime)
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info("Query for Time off requests after %s returns %d results" %(timestamp, len(results_list)))
    return results_list, 200





app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=PORT, debug=True)