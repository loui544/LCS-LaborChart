from etl.classes.rawoffer import rawOffer
from etl.config import *
from statistics import mean
import pika
import re
import json
from etl.classes.enums import educationLevel, contractType
from datetime import datetime
from dagster import get_dagster_logger

logger = get_dagster_logger()

# Elempleo education level dict
elempleoEducationLevels = {
    'Básica Primaria (1° - 5°)': educationLevel.PRIM,
    'Básica Secundaria (6° - 9°)': educationLevel.HIGH,
    'Media (10° - 13°)': educationLevel.HIGH,
    'Técnico Laboral': educationLevel.TECHNIC,
    'Formación Tec profesional': educationLevel.TECHNIC,
    'Tecnológica': educationLevel.TECHNOLOGY,
    'Universitaria': educationLevel.PRE,
    'Especialización': educationLevel.SPEC,
    'Maestría': educationLevel.MASTER
}

# Elempleo contract type dict
elempleoContracts = {
    'Contrato Por obra o labor': contractType.OBR,
    'Contrato Prestacion de Servicios': contractType.PRES,
    'Contrato Indefinido': contractType.INDEF,
    'Contrato Definido': contractType.DEF,
    'Por Horas': contractType.HOR,
    'Tiempo Parcial': contractType.PAR,
    'Tiempo Completo': contractType.COM
}

# Delete from description the substring 'Descripción general'


def cleanDescription(description):
    """
    Remove a specified substring from the given description.

    Args:
        description (str): The input description.
    
    Returns:
        str: The cleaned description.
    """
    return description.replace('Descripción general', '')

# Calculate the salary from the range showed in salary string


def calculateSalary(salary):
    """
    Calculate the average salary from the range shown in the salary string.

    Args:
        salary_string (str): The input salary string containing numeric values.

    Returns:
        int or None: The calculated average salary, or None if no numeric values are found.
    """
    numbers = re.findall(r'\d+\.\d+|\d+', salary.replace(',', '.'))
    numbered = [float(number) for number in numbers]
    if not numbered:
        salary = None
    else:
        calculatedSalary = int(mean(numbered)*1000000)
        salary = calculatedSalary
    return salary

# Transform experience into int


def transformExp(experience):
    """
    Transform experience string into an integer.

    Args:
        experience_string (str): The input experience string containing numeric values.

    Returns:
        int or None: The transformed experience as an integer, or None if no numeric values are found.
    """
    expNumber = re.findall(r'\d+\.\d+|\d+', experience)
    if not expNumber:
        experience = 0
    else:
        experience = [int(number) for number in expNumber][0]
    return experience

# Standardizes the level of education


def standardizeEducationLevel(education):
    """
    Standardize the input education level using a mapping.

    Args:
        education_string (str): The input education level string.

    Returns:
        str or None: The standardized education level or None if no match is found.
    """
    for key, value in elempleoEducationLevels.items():
        if key in education:
            education = value
            break
    return education

# Standardizes the contract type


def standardizeContractType(contract):
    """
    Standardize the input contract type using a mapping.

    Args:
        contract_string (str): The input contract type string.

    Returns:
        str or None: The standardized contract type or None if no match is found.
    """
    for key, value in elempleoContracts.items():
        if key in contract:
            contract = value
            break
    return contract

# Sends offers list to a RabbitMQ queue


def sendList(offers):
    """
    Send a list of offers to a RabbitMQ queue.

    Args:
        offers (List[YourOfferType]): List of offer objects.

    Returns:
        bool: True if the offers are sent successfully, False otherwise.
    """
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(url.RABBITMQ))
        channel = connection.channel()

        channel.queue_declare(queue=rabbitQueue.ELEMPLEO)

        message = json.dumps(
            [offer.__dict__ for offer in offers], ensure_ascii=False)

        channel.basic_publish(
            exchange='', routing_key=rabbitQueue.ELEMPLEO, body=message)
        connection.close()
    except Exception as e:
        raise e


# Normalizes Elempleo offers list


def offersNormalizer(offers):
    """
    Normalize and send a list of offers to a RabbitMQ queue.

    Args:
        offers (List[YourOfferType]): List of offer objects.

    Returns:
        bool: True if the normalization and sending process is successful, False otherwise.
    """
    for off in offers:
        try:
            off.description = cleanDescription(off.description)
            off.salary = calculateSalary(off.salary)
            off.experience = transformExp(off.experience)
            off.education = standardizeEducationLevel(off.education)
            off.contract = standardizeContractType(off.contract)
            off.lowerCase()
        except Exception as e:
            logger.error(f'(LABORCHART) Error: {e}')
    try:
        sendList(offers)
        logger.info(
            '(LABORCHART) Elempleo offers sent successfully to RabbitMQ queue')
    except Exception as e:
        logger.error(
            f'(LABORCHART) Error while trying to send offers to RabbitMQ queue: {e}')
        raise ValueError(e)
