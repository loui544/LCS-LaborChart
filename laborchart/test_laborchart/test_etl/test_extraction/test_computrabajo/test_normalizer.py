from etl.extraction.computrabajo.normalizer import *
from datetime import datetime , timedelta

# Probe the test_calculateSalary when the offer does not have the salary specified
def test_calculateSalary():
    salary = 'convenir'
    salaryProcessed = calculateSalary(salary)
    assert (salaryProcessed == None) 
    
# Probe if the function calculateSalary get the string and filter the value of the offer 
def test_calculateSalary_value():
    salary = "salirio de $1’852.000  según experiencia + prestaciones de ley."
    salaryProcessed = calculateSalary(salary)
    assert (isinstance(salaryProcessed, float))

# Prove if the function transformExp get the string and filter the years of experience 
def test_transformExp():
    experience = '3 años de experiencia'
    experience1 = transformExp(experience)
    assert  (isinstance(experience1, int))
    assert (experience1 == 3)

# Prove if the function transformExp cant distinguish when the value of the exporience is in months
def test_transformExp_month():
    experience = 'mes'
    experience1 = transformExp(experience)
    assert  (experience1 == 0)

# Prove if the function formatDate can take the words that mean the actual date and change the format to a dd-mm-yyyy
def test_formatDate():
    date = "today"
    final_date = formatDate(date)
    date_today = datetime.today()
    date_str = date_today.strftime('%d-%m-%Y')
    assert (final_date == date_str)

# Prove if the function formatDate know when the date they give you is not correct.
def test_formatDate_false():
    date = "today"
    final_date = formatDate(date)
    date_yester = datetime.today()
    yesterday = date_yester - timedelta(days=1)
    date_str = yesterday.strftime('%d-%m-%Y')
    assert not (final_date == date_str)

#Prove that de function standardizeEducationLevel can filter the level of education and it does send any value that is not relevant 
def test_standardizeEducationLevel_filter():
    result = standardizeEducationLevel("Educación mínima:  Bachillerato completo") 
    assert ( result == "Bachillerato completo")

#Prove that the function standardizeEducationLevel take the level of education and assigns it correctly 
def test_standardizeEducationLevel():
    result = standardizeEducationLevel('Educación Básica Primaria')
    assert (result == educationLevel.PRIM)

#Prove that the function standardizeEducationLevel take the level of education and assigns it correctly, by a false case
def test_standardizeEducationLevel_false():
    result = standardizeEducationLevel('Educación Básica Primaria')
    assert not(result == educationLevel.HIGH)

#Prove that the function standardizeContractType take the type of contract  it correctly
def test_standardizeContractType():
    result = standardizeContractType('Contrato civil por prestación de servicios')
    assert (result == contractType.PRES)

#Prove that the function standardizeContractType take the type of contract  it correctly, by a false case
def test_standardizeContractType_false():
    result = standardizeContractType('Contrato civil por prestación de servicios')
    assert not(result == contractType.DEF)


