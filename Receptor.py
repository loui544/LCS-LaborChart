import pika
from pymongo import MongoClient
import json
from Classes.Values import *
from Classes.Values import queue as q


def receiveList():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(uri.RABBITMQ))
        channel = connection.channel()

        queues = [q.ELEMPLEO, q.COMPUTRABAJO]
        offersLists = []

        for queue in queues:

            channel.queue_declare(queue=queue)

            methodFrame, headerFrame, body = channel.basic_get(
                queue=queue, auto_ack=True)

            # If the methodFrame is not None. It means that the queue exist in RabbitMQ
            if methodFrame:
                if body is not None:
                    # decodes offersList in JSON format
                    offersLists.append(json.loads(body.decode('utf-8')))

        connection.close()

        if offersLists:
            print('\nListas de ofertas recibidas de RabbitMQ correctamente\n')
            return offersLists
        else:
            raise ValueError('Error: No hay lista de ofertas en cola')
    except Exception as e:
        raise e


def loadMongoDB(offersLists):
    client = MongoClient(uri.MONGODB)
    try:

        db = client[mongoDB.LABORCHART]
        collection = db[mongoCollection.OFFERS]
        for offerList in offersLists:

            result = collection.insert_many(offerList)
            print('Documentos insertados: ', len(result.inserted_ids))
        client.close()
    except Exception as e:
        client.close()
        raise ValueError('Error: no se pudo cargar a MongoDB', e)


def reception():
    try:
        offersLists = receiveList()
        loadMongoDB(offersLists)
    except Exception as e:
        print(e)
