import pika
from pymongo import MongoClient
import json


def receiveList():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        queues = ['elempleo', 'computrabajo']
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
    uri = 'mongodb://localhost:27017'
    client = MongoClient(uri)
    try:

        db = client['LaborChart']
        collection = db['Offers']
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
