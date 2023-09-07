from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, BulkIndexError
from ETL.Classes.Values import *
from ETL.Config import *
import json


def SendToElasticSearch(offers):
    try:
        es = Elasticsearch(uri.ElasticSearch)
        # offers = json.loads(offers)
        offers = [{'_index': 'laborchart', '_source': offer}
                  for offer in offers]
        success, _ = bulk(es, offers)
        print(success, ' ofertas cargadas exitosamente')

    except BulkIndexError as e:
        raise ValueError('Error: ', e)


try:
    with open('ETL\Transformation\desc.json', 'r', encoding='utf-8') as file:
        offers = json.load(file)
    SendToElasticSearch(offers)
except FileNotFoundError:
    print('Archivo no encontrado')
except Exception as e:
    print('Error: ', e)
