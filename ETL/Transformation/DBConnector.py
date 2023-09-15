from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, BulkIndexError
from ETL.Classes.Values import *
from ETL.Config import *


def sendToElasticSearch(offers):
    try:
        es = Elasticsearch(uri.ElasticSearch)
        offers = [{'_index': 'laborchart', '_source': offer}
                  for offer in offers]
        success, _ = bulk(es, offers)
        print(f'{success} offers succesfully loaded to Elastic Search')

    except BulkIndexError as e:
        raise ValueError('Error: ', e)
