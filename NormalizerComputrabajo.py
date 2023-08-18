from Classes.RawOffer import rawOffer
from statistics import mean
from datetime import datetime
import re
import json

import pika

from Classes.Enums import educationLevel, contractType

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

# extract the float number of the salary in the offer
def CalculateSalary(salary):
    if 'convenir' in salary:
        salary='A convenir'
        return salary
    calculatedSalary = int(''.join(filter(str.isdigit,salary)))
    return calculatedSalary


# extract the integer nunber of the experience in the offer
def TransformExp(experience):
    if 'mes' in experience:
        experience=0
        return experience
        
    expNumber = re.findall(r'\d+\.\d+|\d+', experience)
    if not expNumber:
        experience = 0
    else:
        experience = [int(number) for number in expNumber][0]
    return experience
    
# adjust the date of the offer to the current day
def FormatDate(date):
    try:
        date= datetime.today().strftime('%d-%m-%Y')
        return date
    except Exception as e:
        raise ValueError('Campo date no es correcta (' + str(e) + ')')

# Standardizes the level of education
def StandardizeEducationLevel(education):
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
def StandardizeContractType(contract):
    for key, value in computrabajoContracts.items():
        if key in contract:
            contract = value
            break
    return contract
    
#Send offers list to RabbitMQ queue
def sendList(offers):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='computrabajo')

        message = json.dumps([offer.__dict__ for offer in offers])

        channel.basic_publish(
            exchange='', routing_key='computrabajo', body=message)
        connection.close()
    except Exception as e:
        raise e

#Normalizes Computrabajo offers list
def OffersCleaning(offers):
    for offer in offers:
        try:
            offer.salary = CalculateSalary(offer.salary)
            offer.experience = TransformExp(offer.experience)
            offer.date = FormatDate(offer.date)
            offer.education = StandardizeEducationLevel(offer.education)
            offer.contract = StandardizeContractType(offer.contract)
        except Exception as e:
            raise ValueError('Error: ' + str(e))
    try:
        #sendList(offers)
        
        with open("offers.json", "w",encoding='utf-8') as computrabajo:
            json.dump([offer.__dict__ for offer in offers],computrabajo,ensure_ascii=False,indent=4)
        return 'Lista de ofertas enviada correctamente a la cola de RabbitMQ'
    except Exception as e:
        raise ValueError(
            'Error al enviar las ofertas a la cola de RabbitMQ:' + str(e))
            