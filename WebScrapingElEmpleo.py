from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random

from Classes.RawOffer import rawOffer
from Classes.Time import randomTime

# navigation options
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--log-level=3')

timeRandom = random.uniform(randomTime.MIN, randomTime.MAX)


def offer(driver, lines):
    """
    This function is designed to be sub pages and take all the imformatión that we required, the put it in the instance off the class, instances that we return
    Parameters:

    Generated parameters:

    driver: selenium.webdriver.chrome.webdriver.WebDriver
        Webdriver that is scrolling through the sub-page
    lines: str
        Company name that is better extracting from the main page

    returns:
        returns an instance of the rawOffer class with all parameters filled in, from the path in the page
    """
    try:
        aux = rawOffer
        # do the data collection of the pages
        aux = rawOffer(None, None, None, None, None, None, None, None)
        title = driver.find_element(
            By.XPATH, '/html/body/div[7]/div[1]/div/div[1]/h1/span')
        description = driver.find_element(
            By.CSS_SELECTOR, 'div.description-block')
        salary = driver.find_element(
            By.XPATH, '/html/body/div[7]/div[1]/div/div[1]/div[2]/div[1]/p[1]/span/span[1]')
        education = driver.find_element(
            By.CSS_SELECTOR, 'span.js-education-level')
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
    except Exception:
        pass


def webScraperElempleo():
    """
    This function is designed to obtain the list of offers and open in a second tab the description of offer by offer

    Generated parameters:

    returns:
        returns a list with offers details, of type RawOffer
    """
    try:
        # initialize browser
        url = 'https://www.elempleo.com/co/ofertas-empleo/bogota/hace-1-semana'
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(timeRandom)
        WebDriverWait(driver, 3).until(ec.element_to_be_clickable(
            (By.XPATH, '/html/body/div[8]/div[3]/div[1]/div[3]')))

        # Get all <div> elements inside the parent element using the desired CSS selector
        divElements = driver.find_elements(By.CSS_SELECTOR, 'div.result-item')

        # This part of the code goes through the list that appears on the page
        listOffers = []
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
            aux = offer(driver, lines)
            listOffers.append(aux)

            # switch to tab 1 back and close the previously created tab
            driver.close()
            driver.switch_to.window(openTabs[0])
            time.sleep(timeRandom)
        for div in listOffers:
            print(div)

        print(len(listOffers))
        driver.close()

        return listOffers
    except Exception:
        return ValueError('Error al acceder a la página web')


webScraperElempleo()
