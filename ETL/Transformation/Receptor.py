import pika
import json
from ETL.Config import *
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    filename='Logs/'+datetime.today().strftime('%d-%m-%Y')+'.log'
)


def receiveList():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(url.RABBITMQ))
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
            logging.info(
                f'\n{len(offersList)} offers received successfully from RabbitMQ\n')
            return offersList
        else:
            logging.error('Error: No offers available')
    except Exception as e:
        logging.error(f'Error while trying to connect to RabbitMQ: {e}')


def reception():
    try:
        return receiveList()
    except Exception as e:
        raise ValueError(e)
