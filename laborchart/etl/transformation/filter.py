from etl.transformation.faiss.commons import *
from thefuzz import fuzz
import json
import pandas as pd
from etl.config import *
from dagster import get_dagster_logger

logger = get_dagster_logger()


def filterSimilars(offers, titlesCompanies, model, index):
    """
    Filters similar offers based on titles and companies using a trained model and index.

    Args:
        offers (pd.DataFrame): DataFrame containing offers data.
        titles_companies (list): List of title and company combinations.
        model: Trained SentenceTransformer model.
        index: Trained Faiss index.

    Returns:
        list: Filtered offers in JSON format.

    Raises:
        ValueError: If there are errors during the filtering process.

    Notes:
        This function uses fuzzy string matching to compare title and company combinations.
        Offers with a similarity percentage equal or higher than 95% are considered similar,
        and the second one is deleted.
    """

    deleted = 0
    logger.info(f'(LABORCHART) Initial quantity of offers: {offers.shape[0]}')
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
                        offers = offers.drop(nearIndex)
                        skip.append(nearIndex)
                        deleted += 1
                except Exception as e:
                    logger.error(
                        f'(LABORCHART) Error trying to compare indexes: {e}')
        skip.append(i)

    logger.info(f'(LABORCHART) Deleted: {deleted}')
    logger.info(f'(LABORCHART) Offers left after filter: {offers.shape[0]}')

    # Converts again into JSON list the offers dataframe
    return json.loads(offers.to_json(
        orient='records', force_ascii=False))


def filterOffers(offers):
    """
    Filter similar offers based on their titles and companies.

    Args:
        offers (List[dict]): List of offers.

    Returns:
        List[dict]: Filtered offers.
    """

    try:
        # Converts to dataframe and concatenates title and company
        offers = pd.DataFrame(offers)
        titlesCompanies = (offers['title'].str.replace(
            '\u0301', '') + ' ' + offers['company'].str.replace('\u0301', '')).tolist()
        model, index = modelTraining(titlesCompanies)
        return filterSimilars(offers, titlesCompanies, model, index)
    except Exception as e:
        raise ValueError(e)
