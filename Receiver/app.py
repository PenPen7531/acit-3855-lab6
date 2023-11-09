# Packages for project
import connexion
from connexion import NoContent
import json
import datetime
import os
import requests
import yaml
import logging
import logging.config
from pykafka import KafkaClient
import uuid
import time
from pykafka.exceptions import SocketDisconnectedError, LeaderNotAvailable
# File and Event Constants
EVENT_FILE = 'events.json'
MAX_EVENTS = 10
PORT = 8080


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())






with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def log_action(event):
    "Logs action into log file"

    unique_id = uuid.uuid4()

    logger.info(f'Received event {event} request with a trace id of {unique_id}')

    return unique_id


def log_reponse(event, unique_id, status_code):
    "Logs reponse from Storage"
    logger.info(f'Received event {event} response (ID: {unique_id}) with status code {status_code}')

    

def request_time(body):
    "Request time off for employees. Sends an API request to the DB server to process and store the information"
    
    
    # Sends a post request to the storage/DB program that will save the entries into a DB
    # Specifies the localhost (Can be changed when put into multiple different VMs, content type: json, and the json data sent will be the argument data)
    


    u_id = log_action('Request Time')

    body['trace_id'] = str(u_id)
    
    logger.info(f"Received Event: Trace ID {body['trace_id']}")
   




    producer = topic.get_sync_producer()
    msg = { "type": "time",
    "datetime" :
    datetime.datetime.now().strftime(
    "%Y-%m-%dT%H:%M:%S"),
    "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    # Return NoContent with the reponse code 201
    logger.info(f"Sent Event: Trace ID {body['trace_id']}")
    return NoContent, 201


def add_employee(body):
    "Adds employees to the system. Sends an API request to the DB server to process and store the information"

    u_id = log_action('Add Employee')

    body['trace_id'] = str(u_id)
    logger.info(f"Received Event: Trace ID {body['trace_id']}")
    # Sends a post request to the storage/DB program that will save the entries into a DB
    # Specifies the localhost (Can be changed when put into multiple different VMs, content type: json, and the json data sent will be the argument data)
    
    producer = topic.get_sync_producer()
    msg = {     
        "type": "employee",
        "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body 
    }
    msg_str = json.dumps(msg)

    
    producer.produce(msg_str.encode('utf-8'))
    # Return NoContent with the reponse code 201
    logger.info(f"Sent Event: Trace ID {body['trace_id']}")
    # Returns NoContent with the response code from the DB server
    return NoContent, 201

def connect_kafka():
    "Initializes connection to kafka as a producer"
    try_count = 0 
    
    while try_count <= app_config['kafka']['retries']:
        time.sleep(app_config['kafka']['sleep'])
        logging.info(f"Connecting to Kafka. Try #: {try_count}")
        try:
            client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
            topic = client.topics[str.encode(app_config['events']['topic'])]
            logger.info("Connection Successful")
            # Break loop after connection successful
            break
        except (LeaderNotAvailable, SocketDisconnectedError):
            logging.error(f"Connection Failed. Retrying in {app_config['kafka']['sleep']} seconds")
            time.sleep(app_config['kakfa']['sleep'])
        try_count += 1
    return topic



topic = connect_kafka()
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)




# Runs on Port 8080
if __name__ == "__main__":
    
    app.run(port=PORT)
    
    