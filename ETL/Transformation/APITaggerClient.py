import requests
from ETL.Classes.Values import *
from ETL.Config import *
from datetime import datetime
from pprint import pprint


def client(offers):

    try:
        descriptions = [{"description": offer['description']}
                        for offer in offers]

        response = requests.post(uri.SkillsTaggerAPI, json=descriptions)

        if response.status_code == 200:

            print(
                f'\nSuccessful request. Status code: {response.status_code}\n')
            result = response.json()

            # Removes 'index','start',and 'end' keys
            def removeKeys(x): return {'entities': [{k: v for k, v in entity.items() if k not in [
                'index', 'start', 'end']} for entity in x['entities']]}
            result = {k: removeKeys(v)
                      for k, v in result.items()}

            # Adds labeled entities to each corresponding offer and convert date format from number to date
            for idx, item in enumerate(offers):
                item['date'] = datetime.utcfromtimestamp(
                    item['date']/1000).strftime('%d-%m-%Y')
                if str(idx) in result:
                    item["entities"] = result[str(idx)]["entities"]

            return offers
        else:
            raise ValueError(
                f"Request error. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        raise (f"Connection error: {e}")
