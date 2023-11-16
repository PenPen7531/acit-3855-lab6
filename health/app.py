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


# # Localhost App configuration file
# with open("app_conf.yml", 'r') as f:
#     app_config = yaml.safe_load(f.read())

def get_health():
    "Checks the status of all services"

    try:
        audit_response = requests.get(app_config["services"]["audit"], timeout=5).status_code
    except:
        logging.info("Error requesting to audit service")
        audit_reponse = 500

    try:
        processing_response = requests.get(app_config["services"]["processing"], timeout=5).status_code
    except:
        logging.info("Error with processing service")
        processing_response = 500
    
    try:
        receiver_response = requests.get(app_config["services"]["receiver"], timeout=5).status_code
    except:
        logging.info("Error with receiver service")
        receiver_response = 500
    try:
        storage_response = requests.get(app_config["services"]["storage"], timeout=5).status_code
    except:
        logging.info("Error with storage service")
        storage_response = 500
    audit = "Running" if audit_response == 200 else "Down"
    receiver = "Running" if receiver_response == 200 else "Down"
    processing = "Running" if processing_response == 200 else "Down"
    storage = "Running" if storage_response == 200 else "Down"

    current_date = datetime.datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    health_dict = {
        "receiver": receiver,
        "storage": storage,
        "processing": processing,
        "audit": audit,
        "last_updated": formatted_date
    }
   

    with open(app_config['filename'], "w") as file:
        file.write(json.dumps(health_dict, indent=4))
    return health_dict, 200

# Scheduler configuration
def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(get_health, 'interval', seconds=app_config['schedule_time'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'


if __name__ == "__main__":

    init_scheduler()
    app.run(port=app_config['port'])
    