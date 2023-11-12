from etl.extraction.computrabajo.normalizer import *
from datetime import datetime


def test_calculateSalary():
    salary = None
    calculateSalary(salary)
    assert (salary == None) 
    

def test_calculateSalary_false():
    salary = 100
    calculateSalary(salary)
    assert (isinstance(salary, int))

def test_transformExp():
    experience = 'mes'
    experience1 = transformExp(experience)
    assert  (isinstance(experience1, int))


def test_transformExp_false():
    experience = 'mes'
    experience1 = transformExp(experience)
    assert not (isinstance(experience1, str))



"""
def test_formatDate(monkeypatch):
    pass

def test_formatDate_false():
    pass"""

def test_standardizeEducationLevel_filter():
    result = standardizeEducationLevel("Educación mínima:  Bachillerato completo") 
    assert ( result == "Bachillerato completo")


def test_standardizeEducationLevel():
    result = standardizeEducationLevel('Educación Básica Primaria')
    assert (result == educationLevel.PRIM)


def test_standardizeEducationLevel_false():
    result = standardizeEducationLevel('Educación Básica Primaria')
    assert not(result == educationLevel.HIGH)


def test_standardizeContractType():
    result = standardizeContractType('Contrato civil por prestación de servicios')
    assert (result == contractType.PRES)


def test_standardizeContractType_false():
    result = standardizeContractType('Contrato civil por prestación de servicios')
    assert not(result == contractType.DEF)

"""
def test_offersNormalizer():
    pass

def test_offersNormalizer_false():
    pass
"""
