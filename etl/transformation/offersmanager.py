from etl.transformation.faiss.commons import *
from elasticsearch import Elasticsearch, ConflictError
import pandas as pd
from etl.config import *
from thefuzz import fuzz
from dagster import get_dagster_logger

logger = get_dagster_logger()

es = Elasticsearch(url.ELASTICSEARCH)


def getOffers():
    offersQuantity = es.indices.stats(index=elasticSearch.INDEX)
    if offersQuantity.get('status') is not None:
        if offersQuantity['status'] == 400:
            logger.error(
                f'(LABORCHART) Error: error while trying get total offers in ElasticSearch')
    else:
        if offersQuantity['_all']['primaries']['docs']['count'] == 0:
            logger.info('(LABORCHART) No offers loaded to ElasticSearch')
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
                    logger.error(
                        f'(LABORCHART) Error: error while trying to retrieve offers')
            else:
                offers = []
                for company in resp['aggregations']['unique_categories']['buckets']:
                    offers.extend([{'title': title['key'], 'company': company['key'], 'title company': title['key'] +
                                    ' ' + company['key']} for title in company['unique_categories']['buckets']])
                return offers


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
            logger.error(f'(LABORCHART) Error while trying to update offers')
    else:
        return resp['updated']


def checkSimilars(offers, titlesCompanies, model, index):

    updated = 0
    skip = []
    # For each offer title-company, find the 5 nearest Indexes
    for i, titleCompany in enumerate(titlesCompanies):

        try:
            D, nearestIndexes = index.search(model.encode(
                [titleCompany], show_progress_bar=False), faissParameters.NEAREST)
            nearestIndexes = nearestIndexes[0]
            nearestIndexes = [
                near for near in nearestIndexes if near != i and near not in skip]
        except Exception as e:
            logger.error(
                f'(LABORCHART) Error trying to find nearest indexes: {e}')

        if nearestIndexes:
            # For each offers title-company, compares the string similarity percentage
            for nearIndex in nearestIndexes:

                try:
                    # If offer's title-companies have a pecentage equal or higher of similarity, the second one is deleted
                    if fuzz.ratio(titleCompany, titlesCompanies[nearIndex]) >= 95:
                        logger.info(
                            f'(LABORCHART) ({i}) {titleCompany} <-> ({nearIndex}) {titlesCompanies[nearIndex]}')
                        logger.info(
                            f"(LABORCHART) Similarity percentage: {fuzz.ratio(titleCompany, titlesCompanies[nearIndex])}%")
                        updated += updateOffers(offers.loc[i],
                                                offers.loc[nearIndex])
                        skip.append(nearIndex)
                except Exception as e:
                    logger.error(
                        f'(LABORCHART) Error trying to compare indexes: {e}')
        skip.append(i)

    logger.info(f'(LABORCHART) {updated} offers updated')


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
                logger.error(
                    f'(LABORCHART) Error while trying to update offers')
                return 0
        else:
            return resp['updated']
    except ConflictError as e:
        logger.error(
            f'(LABORCHART) Error while trying to update offers: {e.meta.status}')
        return 0


def checkCompanies(companies, model, index):

    updated = 0
    skip = []
    # For each offer title-company, find the 5 nearest Indexes
    for i, company in enumerate(companies):
        try:
            D, nearestIndexes = index.search(model.encode(
                [company], show_progress_bar=False), faissParameters.NEAREST)
            nearestIndexes = nearestIndexes[0]
            nearestIndexes = [
                near for near in nearestIndexes if near != i and near not in skip]
        except Exception as e:
            logger.error(
                f'(LABORCHART) Error trying to find nearest indexes: {e}')
        if nearestIndexes:
            # For each offers title-company, compares the string similarity percentage
            for nearIndex in nearestIndexes:
                try:
                    # If offer's title-companies have a pecentage equal or higher of similarity, the second one is deleted
                    if fuzz.ratio(company, companies[nearIndex]) >= 85 and fuzz.ratio(company, companies[nearIndex]) < 100:
                        logger.info(
                            f'(LABORCHART) ({i}) {company} <-> ({nearIndex}) {companies[nearIndex]}')
                        logger.info(
                            f"(LABORCHART) Similarity percentage: {fuzz.ratio(company, companies[nearIndex])}%")
                        updated += updateCompany(companies[i],
                                                 companies[nearIndex])
                        skip.append(nearIndex)
                except Exception as e:
                    logger.error(
                        f'(LABORCHART) Error trying to compare indexes: {e}')
        skip.append(i)
    logger.info(f'(LABORCHART) {updated} offers updated')


def offersCheck():
    offers = getOffers()
    offers = pd.DataFrame(offers)
    titlesCompanies = (offers['title company']).tolist()
    model, index = modelTraining(titlesCompanies)
    checkSimilars(offers, titlesCompanies, model, index)
    checkCompanies((offers['company']).tolist(), model, index)
