import requests
from etl.config import *
from dagster import get_dagster_logger

logger = get_dagster_logger()


def client(offers):
    """
    Tag skills in offers by making a POST request to a skill tagging API.

    Args:
        offers (List[dict]): List of offers.

    Returns:
        List[dict]: Processed offers with tagged entities.
    """
    try:
        descriptions = [{"description": offer['description']}
                        for offer in offers]

        response = requests.post(url.SKILLSTAGGERAPI, json=descriptions)

        if response.status_code == 200:

            logger.info(
                f'(LABORCHART) Successful request. Status code: {response.status_code}')
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
            logger.error(
                f"(LABORCHART) Request error. Status code: {response.status_code}")
            raise ValueError(response.status_code)
    except requests.exceptions.RequestException as e:
        logger.error(f"(LABORCHART) Connection error: {e}")
        raise ValueError(e)
