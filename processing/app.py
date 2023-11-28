# Packages for project

import json
import datetime
import os
import logging
import logging.config
import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin
import connexion
from connexion import NoContent


PORT = 8100

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In test environment")
    APP_CONF_FILE = "/config/app_conf.yml"
    LOG_CONF_FILE = "/config/log_conf.yml"
else:
    print("In test environment")
    APP_CONF_FILE = "app_conf.yml"
    LOG_CONF_FILE = "log_conf.yml"

# App configuration file
with open(APP_CONF_FILE, 'r') as f:
    app_config = yaml.safe_load(f.read())


# Log configuration
with open(LOG_CONF_FILE, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info(f"App Conf File: {APP_CONF_FILE}")
logger.info(f"Logging Conf File: {APP_CONF_FILE}")

def health():
    return  'Service Online', 200


def populate_stats():

    # Logs starting periodic processing
    logger.info('Start Periodic Processing')



    # Checks to see if file exists
    if not os.path.isfile(app_config['datastore']['filename']):
        logging.info('No file found. Creating new data.json file')
        # Default values if JSON file is not found
        data = {
            'num_req_off_readings': 0,
            'num_employee_readings': 0,
            'max_days_off': 0, 
            'max_hours_off': 0,
            'last_updated': '2023-01-01T00:00:00Z'
        }



    # If file is found. Use data from this file
    else:    
    # Open file 
        with open(app_config['datastore']['filename'], "r") as file:
            data= json.load(file)
    # Get datetime
    current_date = datetime.datetime.now()

    # Format date time
    formatted_date = current_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Query employee endpoint
    employee_response = requests.get(f"{app_config['eventstore']['url']}/employee?start_timestamp={data['last_updated']}&end_timestamp={formatted_date}"\
                                     , timeout=30)
    
    # Log success or fail status code depending on response
    if employee_response.status_code == 200:
        logger.info(f"Status code 200 recieved by /employee: Retrieved {len(json.loads(employee_response.content))} entries")
    else:
        logger.error('Error: Status Recieved from Storage (/employee) was not 200')
    


    # Query timeoff endpoint
    timeoff_response = requests.get(f"{app_config['eventstore']['url']}/requestleave?start_timestamp={data['last_updated']}&end_timestamp={formatted_date}", timeout=30)


    # Log success or fail status code depdning on reponse
    if timeoff_response.status_code == 200:
        logger.info(f"Status code 200 recieved by /requestleave: Retrieved {len(json.loads(timeoff_response.content))} entries")
    else:
        logger.error('Error: Status Recieved from Storage (/requestleave) was not 200')
    
    

    max_days = 0
    max_hours = 0

    # Get content of timeoff request query
    content = json.loads(timeoff_response.content)
    
    # Loop through all entries
    for dict in content:
        logger.debug(dict)
        if dict['days_off'] > max_days:
            max_days = dict['days_off']

        # Get the maximum number of hours off
        if int(dict['hours_off']) > int(max_hours):
            max_hours = int(dict['hours_off'])

    # Update dictionary
    data['max_days_off'] = max_days
    data['max_hours_off'] = max_hours
    data['num_req_off_readings'] += len(json.loads(timeoff_response.content))
    data['num_employee_readings'] += len(json.loads(employee_response.content))
    data['last_updated']=formatted_date


    # Write content in new into file
    with open(app_config['datastore']['filename'], "w") as file:
        file.write(json.dumps(data, indent=4))

    # Log a debug message with update statistics
    logger.debug(f"\nUpdated Statistics: \n\tNumber of new employee entries: {data['num_employee_readings']}\n\tNumber of new request leave entries: {data['num_req_off_readings']}\n\tMax number off days off:{data['max_days_off']}\n\tMax number of hours off: {data['max_hours_off']}\n\tLast Updated: {formatted_date} ")
    
    # Log a info message indicating period processing has ended
    logger.info('Period Processing has ended')


def get_stats():
    logger.info("Request has started")
    if os.path.isfile(app_config['datastore']['filename']) == False:
        logger.error('404 - Statistics do not exist')
        return "Statistics do not exist", 404
    
    with open(app_config['datastore']['filename'], "r") as file:
        data = json.load(file)
    logger.debug(data)
    logger.info('Request has been completed')
    return data, 200


# Scheduler configuration
def init_scheduler():
    "Starts the scheduler"
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


    
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True, base_path="/processing")
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'



# Runs on Port 8080
if __name__ == "__main__":
    # Starts logger
    init_scheduler()
   
    
    app.run(port=PORT, use_reloader=False)
    

    
    