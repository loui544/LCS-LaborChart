from ETL.Classes.Values import *
from thefuzz import fuzz
import json
import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd
from ETL.Config import *
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    filename='Logs/'+datetime.today().strftime('%d-%m-%Y')+'.log'
)


def modelTraining(offers):
    try:
        # Converts to dataframe and concatenates title and company
        offers = pd.DataFrame(offers)

        titlesCompanies = (offers['title'].str.replace(
            '\u0301', '') + ' ' + offers['company'].str.replace('\u0301', '')).tolist()

        # Encoding title-company list
        model = SentenceTransformer('bert-base-nli-mean-tokens')
        offersEmbeddings = model.encode(
            titlesCompanies, show_progress_bar=True)

        # setting parameters for Product Quantization model
        vectorsDimensionality = offersEmbeddings.shape[1]
        quantizier = faiss.IndexFlatL2(vectorsDimensionality)
        index = faiss.IndexIVFPQ(quantizier, vectorsDimensionality, faissParameters.CLUSTERS,
                                 faissParameters.CENTROIDIDS, faissParameters.CENTROIDBITS)

        # Training and preparing model for production
        index.train(offersEmbeddings)
        index.add(offersEmbeddings)
        index.nprobe = faissParameters.SEARCHSCOPE

        return offers, titlesCompanies, model, index
    except Exception as e:
        logging.error(f'Error trying to train the PQ technic: {e}\n')
        raise ValueError(e)


def filterSimilars(offers, titlesCompanies, model, index):

    deleted = 0
    logging.info(f'Initial quantity of offers: {offers.shape[0]}')
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
            raise ValueError(e)

        if nearestIndexes:
            # For each offers title-company, compares the string similarity percentage
            for nearIndex in nearestIndexes:
                try:
                    # If offer's title-companies have a pecentage equal or higher of similarity, the second one is deleted
                    if fuzz.ratio(titleCompany, titlesCompanies[nearIndex]) >= 95:
                        logging.info(
                            f'({i}) {titleCompany} <-> ({nearIndex}) {titlesCompanies[nearIndex]}')
                        logging.info(
                            f"Similarity percentage: {fuzz.ratio(titleCompany, titlesCompanies[nearIndex])}%")
                        offers = offers.drop(nearIndex)
                        skip.append(nearIndex)
                        deleted += 1
                except Exception as e:
                    logging.error(f'Error trying to compare indexes: {e}')

        else:
            logging.info(
                f'No near indexes found for index ({i}) {titleCompany}')
    skip.append(i)

    logging.info(f'Deleted: {deleted}')
    logging.info(f'Offers left after filter: {offers.shape[0]}')

    # Converts again into JSON list the offers dataframe
    return json.loads(offers.to_json(
        orient='records', force_ascii=False))


def filterOffers(offers):
    try:
        offers, titlesCompanies, model, index = modelTraining(offers)
        return filterSimilars(offers, titlesCompanies, model, index)
    except Exception as e:
        raise ValueError(e)
