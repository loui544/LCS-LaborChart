import pika
from pymongo import MongoClient
import json
from datetime import datetime
from ETL.Config import *


def receiveList():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(uri.RABBITMQ))
        channel = connection.channel()

        queues = rabbitQueue.QUEUES
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
            print('\nOffers received successfully from RabbitMQ\n')
            return offersList
        else:
            raise ValueError('Error: No offers available')
    except Exception as e:
        raise ValueError('Error while trying to connect to RabbitMQ')


def loadMongoDB(offersList):
    client = MongoClient(uri.MONGODB)
    try:

        db = client[mongoDB.DataBase]
        collection = db[mongoDB.Collection]

        # Functions that converts 'date' string field to date type field
        def convertDateType(item): return {
            **item, 'date': datetime.strptime(item['date'], '%d-%m-%Y')}

        # Maps data type convert with offers list
        offersList = list(map(convertDateType, offersList))

        # Stores offers list into MongoDB collection
        result = collection.insert_many(offersList)
        print('Documents loaded to MongoDB: ', len(result.inserted_ids))

        client.close()
    except Exception as e:
        client.close()
        raise ValueError(f"Couldn't load offers to MongoDB successfully: {e}")


def reception():
    try:
        offersList = receiveList()
        loadMongoDB(offersList)
    except Exception as e:
        print(e)
