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
import os
# File and Event Constants
EVENT_FILE = 'events.json'
MAX_EVENTS = 10
PORT = 8080


if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In test environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In test environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

# App configuration file
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())


# Log configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info(f"App Conf File: {app_conf_file}")
logger.info(f"Logging Conf File: {app_conf_file}")


def health():
    return  'Service Online', 200

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
            producer = topic.get_sync_producer()
            logger.info("Connection Successful")

            # Break loop after connection successful
            break
        except (LeaderNotAvailable, SocketDisconnectedError):
            logging.error(f"Connection Failed. Retrying in {app_config['kafka']['sleep']} seconds")
            time.sleep(app_config['kakfa']['sleep'])
        try_count += 1
    return producer




app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)
producer = connect_kafka()



# Runs on Port 8080
if __name__ == "__main__":
    
    app.run(port=PORT)
    
    