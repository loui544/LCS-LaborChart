import requests
from ETL.Config import *
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    filename='Logs/'+datetime.today().strftime('%d-%m-%Y')+'.log'
)


def client(offers):

    try:
        descriptions = [{"description": offer['description']}
                        for offer in offers]

        response = requests.post(url.SKILLSTAGGERAPI, json=descriptions)

        if response.status_code == 200:

            logging.info(
                f'Successful request. Status code: {response.status_code}')
            result = response.json()

            # Removes 'index','start',and 'end' keys
            def removeKeys(x): return {'entities': [{k: v for k, v in entity.items() if k not in [
                'index', 'start', 'end']} for entity in x['entities']]}
            result = {k: removeKeys(v)
                      for k, v in result.items()}

            # Adds labeled entities to each corresponding offer and convert date format from number to date
            for idx, item in enumerate(offers):
                if str(idx) in result:
                    item["entities"] = result[str(idx)]["entities"]

            return offers
        else:
            logging.error(
                f"Request error. Status code: {response.status_code}")
            raise ValueError(response.status_code)
    except requests.exceptions.RequestException as e:
        logging.error(f"Connection error: {e}")
        raise ValueError(e)
