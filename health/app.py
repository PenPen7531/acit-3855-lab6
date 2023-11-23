# Imports

import connexion
from connexion import NoContent
import json
import os
import requests
import yaml
import logging
import logging.config
from flask_cors import CORS, cross_origin
from apscheduler.schedulers.background import BackgroundScheduler
import datetime


# Get configuration files
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


# Setup logger
logger = logging.getLogger('basicLogger')

logger.info(f"App Conf File: {app_conf_file}")
logger.info(f"Logging Conf File: {app_conf_file}")


# # Localhost App configuration file
# with open("app_conf.yml", 'r') as f:
#     app_config = yaml.safe_load(f.read())



# Scheduler function
def update_health():
    "Checks the status of all services"

    # Audit Service Get Request
    try:
        audit_response = requests.get(app_config["services"]["audit"], timeout=5).status_code
    except:
        logging.info("Error requesting to audit service")
        audit_response = 500


    # Processing Service Get Request
    try:
        processing_response = requests.get(app_config["services"]["processing"], timeout=5).status_code
    except:
        logging.info("Error with processing service")
        processing_response = 500
    

    # Receiver Service Get Request
    try:
        receiver_response = requests.get(app_config["services"]["receiver"], timeout=5).status_code
    except:
        logging.info("Error with receiver service")
        receiver_response = 500


    # Storage Service Get Request
    try:
        storage_response = requests.get(app_config["services"]["storage"], timeout=5).status_code
    except:
        logging.info("Error with storage service")
        storage_response = 500

    # If conditions to convert status code to running or down status message
    audit = "Running" if audit_response == 200 else "Down"
    receiver = "Running" if receiver_response == 200 else "Down"
    processing = "Running" if processing_response == 200 else "Down"
    storage = "Running" if storage_response == 200 else "Down"


    # Get current date to track last update time
    current_date = datetime.datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Dictionary 
    health_dict = {
        "receiver": receiver,
        "storage": storage,
        "processing": processing,
        "audit": audit,
        "last_updated": formatted_date
    }
   
    # Put dictionary to json file
    with open(app_config['filename'], "w") as file:
        file.write(json.dumps(health_dict, indent=4))
    return health_dict, 200

def get_health():

    # If file is not found create new file
    if os.path.isfile(app_config['filename']) == False:
        logging.info('No file found. Creating new data.json file')
        # Default values if JSON file is not found
        current_date = datetime.datetime.now()
        formatted_date = current_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Data if no file is found
        data = {
            "receiver": "Receiver Not Found",
            "storage": "Storage Not Found",
            "processing": "Processing Not Found",
            "audit": "Audit Not Found",
            "last_updated": formatted_date
        }



    # If file is found. Use data from this file
    else:    
    # Open file 
        with open(app_config['filename'], "r") as file:
                data= json.load(file)
    return data, 200

# Scheduler configuration
def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(update_health, 'interval', seconds=app_config['schedule_time'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True, base_path="/health")
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'


if __name__ == "__main__":

    init_scheduler()
    app.run(port=app_config['port'])
    