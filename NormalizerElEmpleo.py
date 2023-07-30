from Classes.RawOffer import rawOffer
from statistics import mean
import pika
from datetime import datetime
import re
import json

from Classes.Enums import educationLevel, contractType

elempleoEducationLevels = {
    'Media (10° - 13°)': educationLevel.HIGH,
    'Técnico Laboral': educationLevel.TECHNIC,
    'Formación Tec profesional': educationLevel.TECHNIC,
    'Tecnológica': educationLevel.TECHNOLOGY,
    'Universitaria': educationLevel.PRE,
    'Especialización': educationLevel.SPEC,
    'Maestría': educationLevel.MASTER
}

elempleoContracts = {
    'Contrato Por obra o labor': contractType.OBR,
    'Contrato Prestacion de Servicios': contractType.PRES,
    'Contrato Indefinido': contractType.INDEF,
    'Contrato Definido': contractType.DEF
}

# Delete from description the substring 'Descripción general'


def cleanDescription(description):
    return description.replace('Descripción general', '')

# Calculate the salary from the range showed in salary string


def calculateSalary(salary):
    numbers = re.findall(r'\d+\.\d+|\d+', salary.replace(',', '.'))
    numbered = [float(number) for number in numbers]
    if not numbered:
        salary = 'A convenir'
    else:
        calculatedSalary = int(mean(numbered)*1000000)
        salary = calculatedSalary
    return salary

# Transform experience into int


def transformExp(experience):
    expNumber = re.findall(r'\d+\.\d+|\d+', experience)
    if not expNumber:
        experience = 0
    else:
        experience = [int(number) for number in expNumber][0]
    return experience

# Formats offer's date string into date


def formatDate(date):
    try:
        date = datetime.strptime(date.replace(
            'Publicado ', ''), '%d %b %Y').strftime('%d-%m-%Y')
        return date
    except Exception as e:
        raise ValueError('Campo date no es correcta (' + str(e) + ')')

# Standardizes the level of education


def standardizeEducationLevel(education):
    for key, value in elempleoEducationLevels.items():
        if key in education:
            education = value
            break
    return education

# Standardizes the contract type


def standardizeContractType(contract):
    for key, value in elempleoContracts.items():
        if key in contract:
            contract = value
            break
    return contract

# Sends offers list to a RabbitMQ queue


def sendList(offers):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='elempleo')

        message = json.dumps([offer.__dict__ for offer in offers])

        channel.basic_publish(
            exchange='', routing_key='elempleo', body=message)
        connection.close()
    except Exception as e:
        raise e


# Normalizes Elempleo offers list


def offersCleaning(offers):
    for offer in offers:
        try:
            offer.description = cleanDescription(offer.description)
            offer.salary = calculateSalary(offer.salary)
            offer.experience = transformExp(offer.experience)
            offer.date = formatDate(offer.date)
            offer.education = standardizeEducationLevel(offer.education)
            offer.contract = standardizeContractType(offer.contract)
        except Exception as e:
            raise ValueError('Error: ' + str(e))
    try:
        sendList(offers)
        return 'Lista de ofertas enviada correctamente a la cola de RabbitMQ'
    except Exception as e:
        raise ValueError(
            'Error al enviar las ofertas a la cola de RabbitMQ:' + str(e))
