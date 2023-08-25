import pika
from pymongo import MongoClient
import json
from datetime import datetime
from Classes.Values import *
from Classes.Values import queue as q


def receiveList():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(uri.RABBITMQ))
        channel = connection.channel()

        queues = q.QUEUES
        offersList = []

        for queue in queues:

            channel.queue_declare(queue=queue)

            methodFrame, headerFrame, body = channel.basic_get(
                queue=queue, auto_ack=True)

            # If the methodFrame is not None. It means that the queue exist in RabbitMQ
            if methodFrame:
                if body is not None:
                    # decodes offersList in JSON format
                    offersList.extend(json.loads(body.decode('utf-8')))

        connection.close()

        if offersList:
            print('\nListas de ofertas recibidas de RabbitMQ correctamente\n')
            return offersList
        else:
            raise ValueError('Error: No hay lista de ofertas en cola')
    except Exception as e:
        raise e


def loadMongoDB(offersList):
    client = MongoClient(uri.MONGODB)
    try:

        db = client[mongoDB.LABORCHART]
        collection = db[mongoCollection.OFFERS]

        # Functions that converts 'date' string field to date type field
        def convertDateType(item): return {
            **item, 'date': datetime.strptime(item['date'], '%d-%m-%Y')}

        # Maps data type convert with offers list
        offersList = list(map(convertDateType, offersList))

        # Stores offers list into MongoDB collection
        result = collection.insert_many(offersList)
        print('Documentos insertados: ', len(result.inserted_ids))

        client.close()
    except Exception as e:
        client.close()
        raise ValueError('Error: no se pudo cargar a MongoDB', e)


def reception():
    try:
        offersList = receiveList()
        loadMongoDB(offersList)
    except Exception as e:
        print(e)
