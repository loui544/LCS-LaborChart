from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from ETL.Classes.Values import *

es = Elasticsearch(uri.ElasticSearch)

docs = [
    {
        'title': 'titulo 3',
        'company': 'empresa 3',
        'description': 'descripcion 3',
        'salary': 200000
    },
    {
        'title': 'titulo 4',
        'company': 'empresa 4',
        'description': 'descripcion 4',
        'salary': 200000
    },
    {
        'title': 'titulo 5',
        'company': 'empresa 5',
        'description': 'descripcion 5',
        'salary': 200000
    },
]

docs = [{'_index': 'sample', '_source': doc} for doc in docs]

success, _ = bulk(es, docs)

print(success)

resp = es.search(index='sample', query={'match_all': {}})
print('Hits: ', resp['hits']['total']['value'])
for hit in resp['hits']['hits']:
    print(hit['_source'])
