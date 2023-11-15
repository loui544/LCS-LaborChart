from etl.transformation.faiss.commons import *
from elasticsearch import Elasticsearch, ConflictError
import pandas as pd
from etl.config import *
from thefuzz import fuzz
from dagster import get_dagster_logger

logger = get_dagster_logger()

es = Elasticsearch(url.ELASTICSEARCH)


def getOffers():
    """
    Retrieves offers information from Elasticsearch.

    Returns:
        list: A list of dictionaries containing title, company, and combined title-company information.

    Raises:
        ValueError: If there is an error while trying to retrieve offers from Elasticsearch.

    Notes:
        This function retrieves offers from Elasticsearch and aggregates them by company and title.
    """
    offersQuantity = es.indices.stats(index=elasticSearch.INDEX)
    if offersQuantity.get('status') is not None:
        if offersQuantity['status'] == 400:
            logger.error(
                f'(LABORCHART) Error: error while trying get total offers in ElasticSearch')
            raise ValueError(
                'Error: error while trying get total offers in ElasticSearch')
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
    """
    Updates Elasticsearch offers based on reference information.

    Args:
        reference (dict): The reference offer containing the new title and company information.
        to_change (dict): The offer to be updated, identified by its title and company.

    Returns:
        int: The number of updated offers.

    Raises:
        ValueError: If there is an error while trying to update offers in Elasticsearch.

    Notes:
        This function updates Elasticsearch offers that match the title and company of the 'to_change' offer
        with the new title and company information provided in the 'reference' offer.
    """

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
            raise ValueError('Error while trying to update offers')
    else:
        return resp['updated']


def checkSimilars(offers, titlesCompanies, model, index):
    """
    Checks for similar offers and updates them in the Elasticsearch index.

    Args:
        offers (DataFrame): The DataFrame containing offer information.
        titles_companies (list): The list of concatenated title and company strings.
        model: The SentenceTransformer model for encoding text.
        index: The Faiss index for similarity search.

    Notes:
        This function identifies similar offers based on the 'titles_companies' list,
        compares their string similarity percentage, and updates similar offers in the Elasticsearch index.
    """
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
    """
    Updates the company name in the Elasticsearch index.

    Args:
        reference (str): The new company name to be used as a reference.
        to_change (str): The existing company name to be updated.

    Returns:
        int: The number of updated documents in the Elasticsearch index.

    Raises:
        ValueError: If there is an error while trying to update the offers.

    Notes:
        This function updates documents in the Elasticsearch index where the 'company'
        field matches the specified 'to_change' value, setting the 'company' field to the 'reference' value.
    """
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
                raise ValueError('Error while trying to update offers')
        else:
            return resp['updated']
    except ConflictError as e:
        logger.error(
            f'(LABORCHART) Error while trying to update offers: {e.meta.status}')
        raise ValueError(e.meta.status)


def checkCompanies(companies, model, index):
    """
    Checks and updates similar company names in Elasticsearch index.

    Args:
        companies (List[str]): A list of company names to be checked and updated.
        model: The sentence embedding model used for similarity comparison.
        index: The Faiss index used for nearest neighbor search.

    Raises:
        ValueError: If there is an error while trying to update the offers.

    Notes:
        This function checks for similarity among company names in the provided list.
        If two companies have a similarity percentage between 85 and 99 (inclusive),
        the function updates the Elasticsearch index to use the more common company name.
    """
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
    """
    Retrieves offers from Elasticsearch, checks for similarity among titles and companies,
    and updates the index accordingly.

    Raises:
        ValueError: If there is an error during the offers checking and updating process.

    Notes:
        This function uses the Elasticsearch index to retrieve offers and checks for
        similarity among titles and companies. If two titles or companies have a similarity
        percentage of 95 or higher, the function updates the Elasticsearch index to use
        the more common title or company name.
    """
    try:
        offers = getOffers()
        offers = pd.DataFrame(offers)
        titlesCompanies = (offers['title company']).tolist()
        model, index = modelTraining(titlesCompanies)
        checkSimilars(offers, titlesCompanies, model, index)
        checkCompanies((offers['company']).tolist(), model, index)
    except Exception as e:
        raise ValueError(e)
