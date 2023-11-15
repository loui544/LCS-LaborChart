from etl.classes.rawoffer import rawOffer
from etl.config import *
from datetime import datetime
import re
import json
import pika
from etl.classes.enums import educationLevel, contractType
from datetime import datetime
from dagster import get_dagster_logger

logger = get_dagster_logger()

computrabajoEducationLevels = {
    'Educación Básica Primaria': educationLevel.PRIM,
    'Educación Básica Secundaria': educationLevel.HIGH,
    'Bachillerato / Educación Media': educationLevel.HIGH,
    'Universidad / Carrera técnica': educationLevel.TECHNIC,
    'Universidad / Carrera tecnológica': educationLevel.TECHNOLOGY,
    'Universidad / Carrera Profesional': educationLevel.PRE,
    'Postgrado / Doctorado': educationLevel.DOC,
    'Especialización': educationLevel.SPEC,
    'Maestría': educationLevel.MASTER
}

computrabajoContracts = {
    'Contrato de Obra o labor': contractType.OBR,
    'Contrato civil por prestación de servicios': contractType.PRES,
    'Contrato a término indefinido': contractType.INDEF,
    'Contrato de aprendizaje': contractType.APR,
    'Contrato ocasional de trabajo': contractType.OCAS,
    'Contrato a término fijo': contractType.DEF
}

# Extract the float number of the salary in the offer


def calculateSalary(salary):
    """
    Extracts the float number of the salary in the offer.

    Args:
        salary (str): The salary string.

    Returns:
        float or None: The calculated salary, or None if 'convenir' is in the salary.
    """
    try:
        if 'convenir' in salary:
            salary = None
            return salary
        calculatedSalary = int(''.join(filter(str.isdigit, salary)))/100
        return calculatedSalary
    except:
        salary = None
        return salary


# Extract the integer nunber of the experience in the offer
def transformExp(experience):
    """
    Extracts the integer number of the experience in the offer.

    Args:
        experience (str): The experience string.

    Returns:
        int: The transformed experience value.
    """
    if 'mes' in experience:
        experience = 0
        return experience

    expNumber = re.findall(r'\d+\.\d+|\d+', experience)
    if not expNumber:
        experience = 0
    else:
        experience = [int(number) for number in expNumber][0]
    return experience

# Adjust the date of the offer to the current day


def formatDate(date):
    """
    Adjusts the date of the offer to the current day.

    Args:
        date (str): The date string.

    Returns:
        str: The formatted date.
    """
    try:
        date = datetime.today().strftime('%d-%m-%Y')
        return date
    except Exception as e:
        logger.error(f'(LABORCHART) Incorrect date field ({e})')

# Standardizes the level of education


def standardizeEducationLevel(education):
    """
    Standardizes the level of education.

    Args:
        education (str): The education string.

    Returns:
        educationLevel: The standardized education level.
    """
    valid = education.find("Educación mínima:")
    if valid != -1:
        # Extraemos la parte de la cadena después de "Educación mínima:"
        education = education[valid + len("Educación mínima:"):].strip()
    for key, value in computrabajoEducationLevels.items():
        if key in education:
            education = value
            break
    return education

# Standardizes the contract type


def standardizeContractType(contract):
    """
    Standardizes the contract type.

    Args:
        contract (str): The contract string.

    Returns:
        contractType: The standardized contract type.
    """
    for key, value in computrabajoContracts.items():
        if key in contract:
            contract = value
            break
    return contract

# Send offers list to RabbitMQ queue


def sendList(offers):
    """
    Sends a list of offers to a RabbitMQ queue.

    Args:
        offers (List[rawOffer]): The list of offers to send.
    """
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(url.RABBITMQ))
        channel = connection.channel()

        channel.queue_declare(queue=rabbitQueue.COMPUTRABAJO)

        message = json.dumps(
            [offer.__dict__ for offer in offers], ensure_ascii=False)

        channel.basic_publish(
            exchange='', routing_key=rabbitQueue.COMPUTRABAJO, body=message)
        connection.close()
    except Exception as e:
        raise e

# Normalizes Computrabajo offers list


def offersNormalizer(offers):
    """
    Normalizes a list of Computrabajo offers.

    Args:
        offers (List[rawOffer]): The list of offers to normalize.
    """
    for offer in offers:
        try:
            offer.salary = calculateSalary(offer.salary)
            offer.experience = transformExp(offer.experience)
            offer.date = formatDate(offer.date)
            offer.education = standardizeEducationLevel(offer.education)
            offer.contract = standardizeContractType(offer.contract)
            offer.lowerCase()
        except Exception as e:
            logger.error('(LABORCHART) Error: ' + str(e))
            raise e
    try:
        sendList(offers)
        logger.info(
            '(LABORCHART) Computrabajo offers sent succesfully to RabbitMQ queue')
    except Exception as e:
        logger.error(
            f'(LABORCHART) Error while trying to send offers to RabbitMQ: {e}')
        raise ValueError(e)
