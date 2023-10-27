from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from elasticsearch.helpers import bulk, BulkIndexError
from etl.config import *
from dagster import get_dagster_logger

logger = get_dagster_logger()

es = Elasticsearch(url.ELASTICSEARCH)


def sendToElasticSearch(offers):
    try:
        es.indices.create(index=elasticSearch.INDEX, body={
            "mappings": {
                "properties": {
                    "date": {"type": "date",
                             "format": "dd-MM-yyyy"}
                }
            }
        })
    except RequestError as e:
        if e.error == 'resource_already_exists_exception':
            pass
    try:
        offers = [{'_index': elasticSearch.INDEX, '_source': offer}
                  for offer in offers]
        success, _ = bulk(es, offers)
        logger.info(
            f'(LABORCHART) {success} offers succesfully loaded to Elasticsearch')

    except BulkIndexError as e:
        logger.error(f'(LABORCHART) Error: {e}')
        raise ValueError(e)
