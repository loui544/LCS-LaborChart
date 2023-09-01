from ETL.Classes.Values import *
from thefuzz import fuzz
import json
import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient


def filterLastTwentyDays():
    client = MongoClient(uri.MONGODB)
    try:
        db = client[mongoDB.DataBase]
        collection = db[mongoDB.Collection]

        # Calculates the twenty days ago date
        twentyDaysAgo = datetime.now() - timedelta(days=20)

        # Does the Mongo Query to remove the offers before 20 deays ago
        deleteResult = collection.delete_many({"date": {"$lt": twentyDaysAgo}})
        print(deleteResult.deleted_count, "Documentos eliminados")
    except Exception:
        raise ValueError(
            'Error: error al filtrar las ofertas de los últimos 20 días')


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
        raise ValueError('Error: error al realizar filtrado exacto')


def filterSimilars():
    client = MongoClient(uri.MONGODB)
    try:

        # gets all offers from MongoDB -> 'Laborchart' DB -> 'Offers' collection without '_id' field
        db = client[mongoDB.DataBase]
        collection = db[mongoDB.Collection]
        offers = collection.find({}, {'_id': False})
        client.close()

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
        index = faiss.IndexIVFPQ(quantizier, vectorsDimensionality, faissParameters.VORONOICELLS,
                                 faissParameters.CENTROIDIDS, faissParameters.CENTROIDBITS)

        # Training and preparing model for production
        index.train(offersEmbeddings)
        index.add(offersEmbeddings)
        index.nprobe = faissParameters.SEARCHSCOPE

        # For each offer title-company, find the 5 nearest Indexes
        deleted = 0
        print('Inicialmente hay: ', offers.shape)
        duplicates = []
        for titleCompany in titlesCompanies:
            D, nearestIndexes = index.search(model.encode([titleCompany]),
                                             faissParameters.NEAREST)

            # Deletes the first index, that is the same offer to find
            nearestIndexes = nearestIndexes[0]
            currentIndex = nearestIndexes[0]
            nearestIndexes = nearestIndexes[1:]
            # For each offers title- company, compares the string similarity
            for nearIndex in [x for x in nearestIndexes if x not in duplicates]:
                print(titleCompany + ' <-> ' + titlesCompanies[nearIndex])
                print(fuzz.ratio(titleCompany, titlesCompanies[nearIndex]))
                # If offer's title-companies have a pecentage equal or higher of similarity, the second one is deleted
                if fuzz.ratio(titleCompany, titlesCompanies[nearIndex]) >= 95:
                    offers = offers.drop(nearIndex)
                    duplicates.append(currentIndex)
                    deleted += 1
            print('\n')
        print('Eliminados: ', deleted)

        print('Quedaron: ', offers.shape)

        # Converts again into JSON list the offers dataframe
        offers = json.loads(offers.to_json(
            orient='records', force_ascii=False))

        # Returns just the current day offers
        return list(filter(lambda item: pd.to_datetime(
            int(item['date']), utc=True, unit='ms') == datetime.now(), offers))

    except Exception:
        raise ValueError('Error: error al realizar el filtrado de por PQ')


def filterOffers():
    try:
        # filterLastTwentyDays()
        filterExactDuplicates()
        return filterSimilars()
    except Exception as e:
        raise ValueError(e)


filterExactDuplicates()
