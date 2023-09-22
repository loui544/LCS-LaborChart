import pika
import json
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
            print(f'\n{len(offersList)} offers received successfully from RabbitMQ\n')
            return offersList
        else:
            raise ValueError('Error: No offers available')
    except Exception as e:
        raise ValueError(f'Error while trying to connect to RabbitMQ: {e}')


def reception():
    try:
        return receiveList()
    except Exception as e:
        print(e)
