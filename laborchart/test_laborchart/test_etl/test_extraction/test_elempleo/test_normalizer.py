from etl.extraction.elempleo.normalizer import *

def test_cleanDescription():
   descripcion ='descripción general : ¿Te apasiona el mundo de los deportes? ¿Te gusta trabajar en ambientes dinámicos y retadores?, Si tu respuesta es Sí, te contamos que estamos buscando un: Analista de Tesorería.'
   descripcion1 = cleanDescription(descripcion)
   if descripcion in descripcion1:
       True
   

def test_calculateSalary():
   oferta = "$3,5 a $4 millones"
   offer = calculateSalary(oferta)
   assert (isinstance(offer, int))

def test_calculateSalary_false():
   oferta = "$3,5 a $4 millones"
   offer = calculateSalary(oferta)
   assert not (isinstance(offer, str))


def test_transformExp():
    experience ="2 años de experiencia"
    intExperience = transformExp(experience)
    assert (isinstance(intExperience, int))


def test_transformExp_false():
    experience ="2 años de experiencia"
    intExperience = transformExp(experience)
    assert not (isinstance(intExperience, str))


def test_standardizeEducationLevel():
   result = standardizeEducationLevel('Básica Primaria (1° - 5°)')
   assert (result == educationLevel.PRIM)


def test_standardizeEducationLevel_false():
   result = standardizeEducationLevel('Básica Primaria (1° - 5°)')
   assert not(result == educationLevel.HIGH)


def test_standardizeContractType():
    result = standardizeEducationLevel('Por Horas')
    assert not(result == contractType.HOR)

def test_standardizeContractType_false():
    result = standardizeEducationLevel('Por Horas')
    assert not(result == contractType.PAR)

"""
def test_offersNormalizer():
    pass
def test_offersNormalizer_false():
    pass"""

