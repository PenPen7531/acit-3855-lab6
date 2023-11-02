import connexion
from connexion import NoContent
import json
import os
import requests
import yaml
import logging
import logging.config
from pykafka import KafkaClient
from threading import Thread
from flask_cors import CORS, cross_origin

PORT = 8110

# App configuration file
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


# Log configuration
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')



def get_employee(index):
    """ Get employee based on index """

    
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving employee at index %d" % index)
    employee_list = []
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg["type"] == "employee":
                employee_list.append(msg['payload'])
        data = employee_list[index]
        return data, 200
    except:
        logger.error("No more messages found")
        logger.error("Could not find Employee at index %d" % index)
        return { "message": "Not Found"}, 404
    

def get_request(index):
    """ Get request off record in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving Time Off Request at index %d" % index)
    time_list = []
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg["type"] == "time":
                time_list.append(msg['payload'])
        data = time_list[index]
        return data, 200
    except:
        logger.error("No more messages found")
        logger.error("Could not find BP at index %d" % index)
        return { "message": "Not Found"}, 404
    


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app = connexion.FlaskApp(__name__, specification_dir='')
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
    app.run(port=PORT, host="0.0.0.0")