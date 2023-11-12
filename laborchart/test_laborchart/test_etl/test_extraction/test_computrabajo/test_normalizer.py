from etl.extraction.computrabajo.normalizer import *


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

"""def test_formatDate():
    date  = formatDate("11/11/2023") 
    assert (isinstance(date, datetime))


def test_formatDate_false():
    pass
"""
def test_standardizeEducationLevel():
    result = standardizeEducationLevel("Educación mínima:  Bachillerato completo") 
    assert ( result == "Bachillerato completo")

def test_standardizeEducationLevel_false():
    result = standardizeEducationLevel("Educación mínima:  Bachillerato completo") 
    assert not ( result == "Educación mínima:  Bachillerato completo")

def test_standardizeContractType():
    pass

def test_standardizeContractType_false():
    pass

def test_sendList():
    pass

def test_sendList_false():
    pass

def test_offersNormalizer():
    pass

def test_offersNormalizer_false():
    pass

"""
formatDate
standardizeEducationLevel
standardizeContractType
sendList
offersNormalizer
"""