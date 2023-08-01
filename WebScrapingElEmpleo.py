from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from Classes import *


from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import colorama as c
import time
import random

from Classes.RawOffer import rawOffer


# navigation options
c.init()
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')
# options.add_argument('--allow-running-insecure-content')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--log-level=3')
# options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')

timeRandom = random.uniform(0, 5)
tSleep1 = 1
listOffers = []


def offer():
    """
    This function is designed to be sub pages and take all the imformatión that we required, the put it in the instance off the class, instances that we return
    Parameters:

    Generated parameters:


    returns:
        retorna una instancia de de la clase raw_offer con todos los parametros llenos, del recorrido en la pagina 
    """
    aux = rawOffer
    # do the data collection of the pages
    aux = rawOffer(None, None, None, None, None, None, None, None)
    title = driver.find_element(
        By.XPATH, '/html/body/div[7]/div[1]/div/div[1]/h1/span')
    description = driver.find_element(By.CSS_SELECTOR, 'div.description-block')
    salary = driver.find_element(
        By.XPATH, '/html/body/div[7]/div[1]/div/div[1]/div[2]/div[1]/p[1]/span/span[1]')
    education = driver.find_element(By.CSS_SELECTOR, 'span.js-education-level')
    experience = driver.find_element(
        By.XPATH, '/html/body/div[7]/div[2]/div[1]/div[2]/div[2]/div[2]/p[1]/span')
    contract = driver.find_element(
        By.XPATH, '/html/body/div[7]/div[2]/div[1]/div[2]/div[2]/div[2]/p[2]/span')
    date = driver.find_element(By.CSS_SELECTOR, 'span.js-publish-date')

    # collects the variables and puts them in the auxiliary offer class
    titleText = title.text
    companyText = lines[1]
    descriptionText = description.text
    descriptionsText2 = descriptionText.replace('\n', '')
    salaryText = salary.text
    educacionText = education.text
    experienceText = experience.text
    contractText = contract.text
    dateText = date.text
    aux = rawOffer(titleText, companyText, descriptionsText2, salaryText,
                   educacionText, experienceText, contractText, dateText)

    return aux


# initialize browser
url = 'https://www.elempleo.com/co/ofertas-empleo/bogota/hace-1-semana'

driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(timeRandom)
WebDriverWait(driver, 5).until(ec.element_to_be_clickable(
    (By.XPATH, '/html/body/div[8]/div[3]/div[1]/div[3]')))


# Get all <div> elements inside the parent element using the desired CSS selector
divElements = driver.find_elements(By.CSS_SELECTOR, 'div.result-item')


# This part of the code goes through the list that appears on the page
try:
    for div in divElements:
        aux = rawOffer
        textoDiv = div.text
        lines = textoDiv.split('\n')

        # find the offer link and click opening the page
        link = div.find_element(
            By.CSS_SELECTOR, 'a.text-ellipsis.js-offer-title')
        driver.execute_script("arguments[0].scrollIntoView();", link)
        link.send_keys(Keys.CONTROL + Keys.RETURN)
        time.sleep(timeRandom)

        # change to the recently created page
        openTabs = driver.window_handles
        driver.switch_to.window(openTabs[1])
        time.sleep(timeRandom)

        aux = offer()
        listOffers.append(aux)

        # switch to tab 1 back and close the previously created tab
        driver.close()
        driver.switch_to.window(openTabs[0])
        time.sleep(timeRandom)
except Exception as e:
    print("Error: ", e)

for div in listOffers:
    print(div)

print(len(listOffers))
driver.close()
