from ETL.Classes.Values import *
from thefuzz import fuzz
import json
import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd
from pymongo import MongoClient
from ETL.Config import *


def filterExactDuplicates():
    client = MongoClient(uri.MONGODB)
    # The corresponding query to remove the exact duplicates (exact title and company)
    try:
        db = client[mongoDB.DataBase]

        pipeline = [{"$sort": {"_id": 1}},
                    {
            "$group": {
                "_id": {"title": "$title", "company": "$company"},
                "doc": {"$first": "$$ROOT"}
            }
        },
            {"$replaceRoot": {"newRoot": "$doc"}},
            {"$out": mongoDB.Collection}
        ]

        db[mongoDB.Collection].aggregate(pipeline)

    except Exception:
        raise ValueError('Error: error trying to do exact offers filtering')


def filterSimilars():
    client = MongoClient(uri.MONGODB)
    try:

        # gets all offers from MongoDB -> 'Laborchart' DB -> 'Offers' collection without '_id' field
        db = client[mongoDB.DataBase]
        collection = db[mongoDB.Collection]
        offers = collection.find({}, {'_id': False})

        # Converts to dataframe and concatenates title and company
        offers = pd.DataFrame(offers)

        client.close()

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

    except Exception:
        raise ValueError('Error: error trying to filter by PQ technic')


def deleteOffers():
    client = MongoClient(uri.MONGODB)
    try:
        db = client[mongoDB.DataBase]
        collection = db[mongoDB.Collection]
        # Delete all the current offers in the MongoDB collection
        collection.delete_many({})
        client.close()
    except Exception as e:
        raise ValueError('Error: error trying to delete offers from MongoDB')


def filterOffers():
    try:
        filterExactDuplicates()
        filtered = filterSimilars()
        # TODO quitar o poner comentario cuando sea necesario
        deleteOffers()
        return filtered
    except Exception as e:
        raise ValueError(e)
