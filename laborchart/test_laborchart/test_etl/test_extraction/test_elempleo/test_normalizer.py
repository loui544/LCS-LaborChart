from etl.extraction.elempleo.normalizer import *

#Probe that the function cleanDescription filter the titlel that Elempleo portal put in all the offers 
def test_cleanDescription():
   descripcion ='Descripción general ¿Te apasiona el mundo de los deportes? ¿Te gusta trabajar en ambientes dinámicos y retadores?, Si tu respuesta es Sí, te contamos que estamos buscando un: Analista de Tesorería.'
   descripcion1 = cleanDescription(descripcion)
   assert (descripcion1 == " ¿Te apasiona el mundo de los deportes? ¿Te gusta trabajar en ambientes dinámicos y retadores?, Si tu respuesta es Sí, te contamos que estamos buscando un: Analista de Tesorería.")
   
# Probe that the function calculateSalary can take the string of a offer of Elempleo portal and filter the value and this value is correct 
def test_calculateSalary():
   oferta = "$3,5 a $4 millones"
   offer = calculateSalary(oferta)
   assert (isinstance(offer, int))
   assert (offer == 3750000)

# Probe that the function calculateSalary can take the string of a offer of Elempleo portal and filter the value and this value is correct, by a false case
def test_calculateSalary_false():
   oferta = "$3,5 a $4 millones"
   offer = calculateSalary(oferta)
   assert not (isinstance(offer, str))

# Probe that the function transformExp get the string and filter the years of experience
def test_transformExp():
    experience ="2 años de experiencia"
    intExperience = transformExp(experience)
    assert (isinstance(intExperience, int))
    assert (intExperience == 2)

# Probe that the function transformExp get the string and filter the years of experience by a false case
def test_transformExp_false():
    experience ="2 años de experiencia"
    intExperience = transformExp(experience)
    assert not (isinstance(intExperience, str))
    assert not (intExperience == 1)

# Probe that the function standardizeEducationLevel take the level of education and assigns it correctly
def test_standardizeEducationLevel():
   result = standardizeEducationLevel('Básica Primaria (1° - 5°)')
   assert (result == educationLevel.PRIM)

# Probe that the function standardizeEducationLevel take the level of education and assigns it correctly, by a false case
def test_standardizeEducationLevel_false():
   result = standardizeEducationLevel('Básica Primaria (1° - 5°)')
   assert not(result == educationLevel.HIGH)

# Prove that the function standardizeContractType take the type of contract and assigns it correctlyn
def test_standardizeContractType():
    result = standardizeContractType('Contrato Por obra o labor')
    assert (result == contractType.OBR)

# Probe that the function standardizeContractType take the type of contract and assigns it correctlyn, by a false case
def test_standardizeContractType_false():
    result = standardizeContractType('Contrato Por obra o labor')
    assert not(result == contractType.PAR)


