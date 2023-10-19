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
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread






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



def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event',reset_offset_on_start=False,auto_offset_reset=OffsetType.LATEST)
    
    trace_ids = []
    
    # This is blocking - it will wait for a new message
    for msg in consumer:
        session = DB_SESSION()
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        # logger.info("Message:%s" % msg)
        payload = msg["payload"]
        logger.info("Message: %s" % msg)
        if payload['trace_id'] not in trace_ids:
            trace_ids.append(payload['trace_id'])
            if msg["type"] == "time": # Change this to your event type
            # # Store the event1 (i.e., the payload) to the DB
                
                
                logger.info("Adding Request Off")
                # Creates the SQL entry from python information
                data = RequestLeave(  payload['trace_id'],
                                    payload['employee_id'],
                                    payload['days_off'],
                                    payload['start_date'],
                                    payload['end_date'],
                                    payload['hours_off'],
                                    payload['reason'])

                

            
            
                

        
        
            elif msg["type"] == "employee": # Change this to your event type
                # Store the event2 (i.e., the payload) to the DB

            
                logger.info("Adding Employee")
                # Creates the SQL entry from python information
                data = Employee(
                    payload['trace_id'],
                    payload['employee_id'],
                    payload['address'],
                    payload['birth_date'],
                    payload['first_name'],
                    payload['last_name'],
                    payload['manager_code'],
                    payload['phone_number'],
                    payload['position'],
                    payload['salary']
                )
                
            # Adds entry to the table
            session.add(data)

                


                
        logger.info("Data has been entered")
        # Commit the new message as being read
        session.commit()
        session.close()
        consumer.commit_offsets()



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    t1=Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=PORT, host="0.0.0.0")