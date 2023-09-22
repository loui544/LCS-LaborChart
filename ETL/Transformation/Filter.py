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

        titlesCompanies = (offers['title'].str.replace('\u0301','') + ' ' + offers['company'].str.replace('\u0301','')).tolist()

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
    except Exception as e:
        raise ValueError(f'\nError trying to train the PQ technic: {e}\n')
    
    print(f'\nInitial quantity of offers: {offers.shape[0]}\n')
    skip = []
    # For each offer title-company, find the 5 nearest Indexes
    for i, titleCompany in enumerate(titlesCompanies):
        try:
            D, nearestIndexes = index.search(model.encode([titleCompany]),
                                             faissParameters.NEAREST)
            nearestIndexes = nearestIndexes[0]
            nearestIndexes = [
                near for near in nearestIndexes if near != i and near not in skip]
            print(f'\nNearest indexes: {nearestIndexes}')
        except Exception as e:
            print(f'\nError trying to find nearest indexes: {e}\n')

        if nearestIndexes:
            print(f'Near indexes found for ({i}) {titleCompany}\n')
            # For each offers title-company, compares the string similarity percentage
            for nearIndex in nearestIndexes:
                try:
                    try: 
                        print(f'({i}) {titleCompany} <-> ({nearIndex}) {titlesCompanies[nearIndex]}')
                        print(f"Similarity percentage: {fuzz.ratio(titleCompany, titlesCompanies[nearIndex])}%")
                    except Exception as e:
                        print(f'\nError al imprimir comparasión de ofertas y porcentaje de similitud {e}\n')
                    # If offer's title-companies have a pecentage equal or higher of similarity, the second one is deleted
                    try:
                        if fuzz.ratio(titleCompany, titlesCompanies[nearIndex]) >= 95:
                            offers = offers.drop(nearIndex)
                            skip.append(nearIndex)
                            deleted += 1
                    except Exception as e:
                        print(f'\nError al hacer condición de porcentaje de similitud: {e}\n')
                    skip.append(i)
                except Exception as e:
                    print(f'\nError trying to compare indexes: {e}\n')
        else:
            print(f'\nNo near indexes found for index ({i}) {titleCompany}')
            
    print(f'\nDeleted: {deleted}')
    print(f'Offers left after filter: {offers.shape[0]}\n')
    # Converts again into JSON list the offers dataframe
    return json.loads(offers.to_json(
        orient='records', force_ascii=False))


def filterOffers(offers):
    try:
        return filterSimilars(offers)
    except Exception as e:
        raise ValueError(e)