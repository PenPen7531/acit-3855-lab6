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

import uuid

# File and Event Constants
EVENT_FILE = 'events.json'
MAX_EVENTS = 10
PORT = 8080


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())




# WORK ON THIS! FSS

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

    response = requests.post(app_config['eventstore1']['url'], headers={'Content-type': 'application/json'}, json=body)

    log_reponse('Request Time', u_id, response.status_code)
    

    # Return NoContent with the reponse code from the DB server
    return NoContent, response.status_code


def add_employee(body):
    "Adds employees to the system. Sends an API request to the DB server to process and store the information"

    u_id = log_action('Add Employee')

    body['trace_id'] = str(u_id)

    # Sends a post request to the storage/DB program that will save the entries into a DB
    # Specifies the localhost (Can be changed when put into multiple different VMs, content type: json, and the json data sent will be the argument data)
    response = requests.post(app_config['eventstore2']['url'], headers={'Content-type': 'application/json'}, json=body)

    

    log_reponse('Add Employee', u_id, response.status_code)
    
    # Returns NoContent with the response code from the DB server
    return NoContent, response.status_code



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)




# Runs on Port 8080
if __name__ == "__main__":
    app.run(port=PORT, debug = True)
    
    