import pika
import json
from etl.config import *
from dagster import get_dagster_logger

logger = get_dagster_logger()


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
            logger.info(
                f'(LABORCHART) {len(offersList)} offers received successfully from RabbitMQ')
            return offersList
        else:
            logger.error('(LABORCHART) Error: No offers available')
            raise ValueError('Error: No offers available')
    except Exception as e:
        logger.error(
            f'(LABORCHART) Error while trying to connect to RabbitMQ: {e}')
        raise ValueError(e)


def reception():
    try:
        return receiveList()
    except Exception as e:
        raise ValueError(e)
