from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import time
import random
import os

from Classes.RawOffer import rawOffer

# Add browser drivers to PATH
os.environ['PATH'] += r"C:/SeleniumDrivers"

# navigation options
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--log-level=3')

timeRandom = random.uniform(2, 4)

# Read the a offer
def Offer(box_details, date):
    try:
        aux = rawOffer
        # do the data collection of the pages
        aux = rawOffer(None, None, None, None, None, None, None, None)
        
        title = box_details.find_element(
            By.CSS_SELECTOR, 'p.title_offer').text
        try:
            company = box_details.find_element(
                By.XPATH, 'div[1]/div[1]/a').text
        except:
            company='Importante empresa del sector'
        description = box_details.find_element(
            By.CSS_SELECTOR, 'body > main > div.box_border.menu_top > div > div.dFlex.dIB_m.w100_m > div:nth-child(2) > div:nth-child(7) > div:nth-child(1) > div.fs16').text.replace('\n', ' ')
        salary = box_details.find_element(
            By.CSS_SELECTOR, 'span.tag base mb10'.replace(' ', '.')).text
        requirements = box_details.find_elements(By.CSS_SELECTOR, 'li.mb5')
        education=requirements[0].text
        if len(requirements)>1:
            if 'experiencia' in requirements[1].text:
                experience=requirements[1].text
            else:
                experience='mes'
        contract= box_details.find_element(
            By.CSS_SELECTOR,'body > main > div.box_border.menu_top > div > div.dFlex.dIB_m.w100_m > div:nth-child(2) > div:nth-child(7) > div:nth-child(1) > div.fs14.mb10 > div > span:nth-child(2)').text
        
        aux = rawOffer(title, company, description, salary,education, experience, contract, date)

        return aux
    except :
        pass

# Read all the offerts main page
def WebScraperComputrabajo():

    # Page initializer
    try:
    # Computrabajo URL of the last post in the last 7 days
        url = 'https://co.computrabajo.com/empleos-en-bogota-dc?pubdate=7&by=publicationtime&p='

        # Initializa the web driver
        driver = webdriver.Chrome(options=options)
        
        time.sleep(timeRandom)

        #List of offers
        listOffers = []
        
        # Iterate each offert in a page
        page=1
        for tab in range(455):
            # Set the url, adding the page to start
            driver.get(url+str(page))
            # Get box_offer class elements
            box_offers = driver.find_elements(By.CLASS_NAME, 'box_offer')
            ids = []

            # Get the offers id of those with company name public
            for offer in box_offers:
                ids.append(offer.get_attribute('data-id'))

            # Get info of the offer 
            for i in range(len(ids)):
                # Select the offer to extract information
                box = box_offers[i]
                #Get the date of the offer
                date=box.find_element(By.CLASS_NAME,'fc_aux').text
                box.click()

                #End the program and send the raw_offers
                if 'día' in date:
                    return listOffers
        
                # Define the element to read
                box_details = driver.find_element(
                    By.CSS_SELECTOR, 'div.box_detail')
                
                time.sleep(timeRandom)
                aux=Offer(box_details,date)
                listOffers.append(aux)

            # Click button to the next page offer
            nextButton = driver.find_element(
                By.XPATH, '/html/body/main/div[6]/div/div[2]/div[1]/div[7]/span[2]')
            nextButton.click()
            
            page+=1
        for div in listOffers:
            print(div)
        driver.close()
        print(len(listOffers))
        listOffers=list(filter(None,listOffers))
        
        return listOffers
    except Exception:
        ValueError('Error al acceder a la pagina web')
        
#WebScraperComputrabajo()