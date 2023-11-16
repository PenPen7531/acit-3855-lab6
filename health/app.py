import connexion
from connexion import NoContent
import json
import os
import requests
import yaml
import logging
import logging.config


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

    
    audit_response = requests.get(app_config["services"]["audit"], timeout=5)
    processing_response = requests.get(app_config["services"]["processing"], timeout=5)
    receiver_response = requests.get(app_config["services"]["receiver"], timeout=5)
    storage_response = requests.get(app_config["services"]["storage"], timeout=5)

    health_dict = {
        "receiver": receiver_response.status_code,
        "storage": storage_response.status_code,
        "processing": processing_response.status_code,
        "audit": audit_response.status_code
    }

    return health_dict, 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=app_config['port'])
    # app.run(port=8120)