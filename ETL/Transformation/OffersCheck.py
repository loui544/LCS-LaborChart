from elasticsearch import Elasticsearch, ConflictError
import pandas as pd
from ETL.Config import *
import faiss
from sentence_transformers import SentenceTransformer
from ETL.Classes.Values import *
from thefuzz import fuzz
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    filename='Logs/'+datetime.today().strftime('%d-%m-%Y')+'.log'
)

es = Elasticsearch(url.ELASTICSEARCH)


def getOffers():
    offersQuantity = es.indices.stats(index=elasticSearch.INDEX)
    if offersQuantity.get('status') is not None:
        if offersQuantity['status'] == 400:
            logging.error(
                f'Error: error while trying get total offers in ElasticSearch')
    else:
        if offersQuantity['_all']['primaries']['docs']['count'] == 0:
            logging.info('No offers loaded to ElasticSearch')
        else:
            aggQuery = {
                "unique_categories": {
                    "terms": {
                        "field": "company.keyword",
                        "size": offersQuantity['_all']['primaries']['docs']['count']
                    }, "aggs": {
                        "unique_categories": {
                            "terms": {
                                "field": "title.keyword"
                            }
                        }
                    }
                }
            }

            resp = es.search(index=elasticSearch.INDEX, aggs=aggQuery)
            if resp.get('status') is not None:
                if resp['status'] == 400:
                    logging.error(
                        f'Error: error while trying to retrieve offers')
            else:
                titlesCompanies = []
                for company in resp['aggregations']['unique_categories']['buckets']:
                    titlesCompanies.extend([{'title': title['key'], 'company': company['key'], 'title company': title['key'] +
                                             ' ' + company['key']} for title in company['unique_categories']['buckets']])

                titlesCompanies = pd.DataFrame(titlesCompanies)
                return titlesCompanies


def modelTraining(titlesCompanies):
    try:
        titlesCompaniesDf = titlesCompanies
        titlesCompanies = (titlesCompanies['title company']).tolist()
        # Encoding title-company list
        model = SentenceTransformer('bert-base-nli-mean-tokens')
        offersEmbeddings = model.encode(titlesCompanies)

        # setting parameters for Product Quantization model
        vectorsDimensionality = offersEmbeddings.shape[1]
        quantizier = faiss.IndexFlatL2(vectorsDimensionality)
        index = faiss.IndexIVFPQ(quantizier, vectorsDimensionality, faissParameters.CLUSTERS,
                                 faissParameters.CENTROIDIDS, faissParameters.CENTROIDBITS)

        # Training and preparing model for production
        index.train(offersEmbeddings)
        index.add(offersEmbeddings)
        index.nprobe = faissParameters.SEARCHSCOPE

        return titlesCompaniesDf, titlesCompanies, model, index
    except Exception as e:
        logging.error(f'Error trying to train the PQ technic: {e}')


def updateOffers(reference, toChange):

    query = {
        'bool': {
            'must': [
                {'match_phrase': {'title': toChange['title']}},
                {'match_phrase': {'company': toChange['company']}}
            ]
        }
    }

    script = {
        'source': f"""ctx._source.title = '{reference['title']}';
                ctx._source.company = '{reference['company']}';""",
        'lang': 'painless'
    }

    resp = es.update_by_query(
        index=elasticSearch.INDEX, query=query, script=script)

    if resp.get('status') is not None:
        if resp['status'] >= 400:
            logging.error(f'Error while trying to update offers')
    else:
        return resp['updated']


def checkSimilars(titlesCompaniesDf, titlesCompanies, model, index):

    updated = 0
    skip = []
    # For each offer title-company, find the 5 nearest Indexes
    for i, titleCompany in enumerate(titlesCompanies):

        try:
            D, nearestIndexes = index.search(model.encode([titleCompany]),
                                             faissParameters.NEAREST)
            nearestIndexes = nearestIndexes[0]
            nearestIndexes = [
                near for near in nearestIndexes if near != i and near not in skip]
        except Exception as e:
            logging.error(f'Error trying to find nearest indexes: {e}')

        if nearestIndexes:
            # For each offers title-company, compares the string similarity percentage
            for nearIndex in nearestIndexes:

                try:
                    # If offer's title-companies have a pecentage equal or higher of similarity, the second one is deleted
                    if fuzz.ratio(titleCompany, titlesCompanies[nearIndex]) >= 95:
                        logging.info(
                            f'Near index found for ({i}) {titleCompany}')
                        logging.info(
                            f'({i}) {titleCompany} <-> ({nearIndex}) {titlesCompanies[nearIndex]}')
                        logging.info(
                            f"Similarity percentage: {fuzz.ratio(titleCompany, titlesCompanies[nearIndex])}%")
                        updated += updateOffers(titlesCompaniesDf.loc[i],
                                                titlesCompaniesDf.loc[nearIndex])
                        skip.append(nearIndex)
                except Exception as e:
                    logging.error(f'Error trying to compare indexes: {e}')
        skip.append(i)

    logging.info(f'{updated} offers updated')


def updateCompany(reference, toChange):
    query = {
        'bool': {
            'must': [
                {'match_phrase': {'company': toChange}}
            ]
        }
    }

    script = {
        'source': f"ctx._source.company = '{reference}';",
        'lang': 'painless'
    }
    try:
        resp = es.update_by_query(
            index=elasticSearch.INDEX, query=query, script=script)
        if resp.get('status') is not None:
            if resp['status'] == 400:
                logging.error(f'Error while trying to update offers')
                return 0
        else:
            return resp['updated']
    except ConflictError as e:
        logging.error(f'Error while trying to update offers: {e.meta.status}')
        return 0


def checkCompanies(companies, model, index):

    updated = 0
    skip = []
    # For each offer title-company, find the 5 nearest Indexes
    for i, company in enumerate(companies):
        try:
            D, nearestIndexes = index.search(model.encode([company]),
                                             faissParameters.NEAREST)
            nearestIndexes = nearestIndexes[0]
            nearestIndexes = [
                near for near in nearestIndexes if near != i and near not in skip]
        except Exception as e:
            logging.error(f'Error trying to find nearest indexes: {e}')
        if nearestIndexes:
            # For each offers title-company, compares the string similarity percentage
            for nearIndex in nearestIndexes:
                try:
                    # If offer's title-companies have a pecentage equal or higher of similarity, the second one is deleted
                    if fuzz.ratio(company, companies[nearIndex]) >= 85 and fuzz.ratio(company, companies[nearIndex]) < 100:
                        logging.info(
                            f'Near index found for ({i}) {company}({i}) {company} <-> ({nearIndex}) {companies[nearIndex]}')
                        logging.info(
                            f"Similarity percentage: {fuzz.ratio(company, companies[nearIndex])}%")
                        updated += updateCompany(companies[i],
                                                 companies[nearIndex])
                        skip.append(nearIndex)
                except Exception as e:
                    logging.error(f'Error trying to compare indexes: {e}')
        skip.append(i)
    logging.info(f'{updated} offers updated')


def offersCheck():
    titlesCompanies = getOffers()
    titlesCompaniesDf, titlesCompanies, model, index = modelTraining(
        titlesCompanies)
    checkSimilars(titlesCompaniesDf, titlesCompanies, model, index)
    checkCompanies((titlesCompaniesDf['company']).tolist(), model, index)
