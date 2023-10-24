from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, BulkIndexError
from etl.config import *
from dagster import get_dagster_logger

logger = get_dagster_logger()


def sendToElasticSearch(offers):
    try:
        es = Elasticsearch(url.ELASTICSEARCH)
        offers = [{'_index': elasticSearch.INDEX, '_source': offer}
                  for offer in offers]
        success, _ = bulk(es, offers)
        logger.info(
            f'(LABORCHART) {success} offers succesfully loaded to Elasticsearch')

    except BulkIndexError as e:
        logger.critical('(LABORCHART) Error: ', e)
        raise ValueError(e)
