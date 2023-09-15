from ETL.Classes.RawOffer import rawOffer
from ETL.Config import *
from statistics import mean
from datetime import datetime
import re
import json
from ETL.Classes.Values import *
import pika
from ETL.Classes.Enums import educationLevel, contractType

computrabajoEducationLevels = {
    'Educación Básica Primaria': educationLevel.HIGH,
    'Bachillerato / Educación Media': educationLevel.HIGH,
    'Universidad / Carrera técnica': educationLevel.TECHNIC,
    'Universidad / Carrera tecnológica': educationLevel.TECHNOLOGY,
    'Universidad / Carrera Profesional': educationLevel.PRE,
    'Especialización': educationLevel.SPEC,
    'Maestría': educationLevel.MASTER
}

computrabajoContracts = {
    'Contrato de Obra o labor': contractType.OBR,
    'Contrato civil por prestación de servicios': contractType.PRES,
    'Contrato a término indefinido': contractType.INDEF,
    'Contrato a término fijo': contractType.DEF
}

# Extract the float number of the salary in the offer


def calculateSalary(salary):
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
    try:
        date = datetime.today().strftime('%d-%m-%Y')
        return date
    except Exception as e:
        raise ValueError(f'Incorrect date field ({e})')

# Standardizes the level of education


def standardizeEducationLevel(education):
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
    for key, value in computrabajoContracts.items():
        if key in contract:
            contract = value
            break
    return contract

# Send offers list to RabbitMQ queue


def sendList(offers):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(uri.RABBITMQ))
        channel = connection.channel()

        channel.queue_declare(queue=rabbitQueue.COMPUTRABAJO)

        message = json.dumps([offer.__dict__ for offer in offers])

        channel.basic_publish(
            exchange='', routing_key=rabbitQueue.COMPUTRABAJO, body=message)
        connection.close()
    except Exception as e:
        raise e

# Normalizes Computrabajo offers list


def offersNormalizer(offers):

    for offer in offers:
        try:
            offer.salary = calculateSalary(offer.salary)
            offer.experience = transformExp(offer.experience)
            offer.date = formatDate(offer.date)
            offer.education = standardizeEducationLevel(offer.education)
            offer.contract = standardizeContractType(offer.contract)
        except Exception as e:
            raise ValueError('Error: ' + str(e))
    try:
        sendList(offers)
        print('\nOffers sent succesfully to RabbitMQ queue\n')
    except Exception as e:
        raise ValueError(f'Error while trying to send offer to RabbitMQ: {e}')
