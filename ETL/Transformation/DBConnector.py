from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, BulkIndexError
from ETL.Config import *
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    filename='Logs/'+datetime.today().strftime('%d-%m-%Y')+'.log'
)


def sendToElasticSearch(offers):
    try:
        es = Elasticsearch(url.ELASTICSEARCH)
        offers = [{'_index': elasticSearch.INDEX, '_source': offer}
                  for offer in offers]
        success, _ = bulk(es, offers)
        logging.info(f'{success} offers succesfully loaded to Elastic Search')

    except BulkIndexError as e:
        logging.critical('Error: ', e)
        raise ValueError(e)
