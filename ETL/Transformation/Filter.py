from ETL.Classes.Values import *
from thefuzz import fuzz
import json
import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd
from ETL.Config import *


def filterSimilars(offers):
    try:
        # Converts to dataframe and concatenates title and company
        offers = pd.DataFrame(offers)

        pd.set_option('display.max_columns', None)
        titlesCompanies = (offers['title'] + ' ' + offers['company']).tolist()

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

        deleted = 0
        print(f'\nInitial quantity of offers: {offers.shape[0]}\n')

        skip = []
        # For each offer title-company, find the 5 nearest Indexes
        for i, titleCompany in enumerate(titlesCompanies):
            D, nearestIndexes = index.search(model.encode([titleCompany]),
                                             faissParameters.NEAREST)

            nearestIndexes = nearestIndexes[0]
            nearestIndexes = [
                near for near in nearestIndexes if near != i and near not in skip]
            if nearestIndexes:
                print(f'\nNear indexes found for index #{i}')
                # For each offers title-company, compares the string similarity percentage
                for nearIndex in nearestIndexes:
                    print(
                        f'({i}) {titleCompany} <-> ({nearIndex}) {titlesCompanies[nearIndex]}')
                    print(
                        f"Similarity percentage: {fuzz.ratio(titleCompany, titlesCompanies[nearIndex])}%")
                    # If offer's title-companies have a pecentage equal or higher of similarity, the second one is deleted
                    if fuzz.ratio(titleCompany, titlesCompanies[nearIndex]) >= 95:
                        offers = offers.drop(nearIndex)
                        skip.append(nearIndex)
                        deleted += 1
                    skip.append(i)
            else:
                print(f'\nNo near indexes found for index #{i}')

        print(f'\nDeleted: {deleted}')
        print(f'Offers left after filter: {offers.shape[0]}\n')

        # Converts again into JSON list the offers dataframe
        return json.loads(offers.to_json(
            orient='records', force_ascii=False))

    except Exception as e:
        raise ValueError(f'Error: error trying to filter by PQ technic: {e}')


def filterOffers(offers):
    try:
        return filterSimilars(offers)
    except Exception as e:
        raise ValueError(e)
