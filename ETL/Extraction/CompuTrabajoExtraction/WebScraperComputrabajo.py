from selenium import webdriver
from selenium.webdriver.common.by import By
from ETL.Config import *
from ETL.Classes.RawOffer import rawOffer
from ETL.Classes.Values import *
import time
import random
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    filename='Logs/'+datetime.today().strftime('%d-%m-%Y')+'.log'
)


# navigation options
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--log-level=3')


def randomSleep():
    return random.uniform(times.MIN, times.MAX)

# Read the a offer


def Offer(box_details, date):
    try:
        aux = rawOffer
        # do the data collection of the pages
        aux = rawOffer(None, None, None, None, None, None, None, None)

        # Get the title of the offer
        try:
            title = box_details.find_element(
                By.CSS_SELECTOR, 'p.title_offer').text
        except:
            logging.error('Title element from Computrabajo not found')
            return None

        # Get the name of the company
        try:
            company = box_details.find_element(
                By.XPATH, 'div[1]/div[1]/a').text
        except:
            logging.error('Company element from Computrabajo not found')
            company = 'Empresa confidencial'

        # Get the description of the offer
        try:
            description = box_details.find_element(
                By.CSS_SELECTOR, 'body > main > div.box_border.menu_top > div > div.dFlex.dIB_m.w100_m > div:nth-child(2) > div:nth-child(7) > div:nth-child(1) > div.fs16').text.replace('\n', ' ')
        except:
            logging.error('Description element from Computrabajo not found')
            return None

        # Get the salary of the offer
        try:
            salary = box_details.find_element(
                By.CSS_SELECTOR, 'span.tag base mb10'.replace(' ', '.')).text
        except:
            logging.error('Salary element from Computrabajo not found')
            return None
        # Get the requirements of the offer
        try:
            requirements = box_details.find_elements(By.CSS_SELECTOR, 'li.mb5')
            education = requirements[0].text
            if len(requirements) > 1:
                if 'experiencia' in requirements[1].text:
                    experience = requirements[1].text
                else:
                    experience = 'mes'
        except:
            logging.error('Requirements element from Computrabajo not found')
            return None

        # Get the contract type
        try:
            contract = box_details.find_element(
                By.CSS_SELECTOR, 'body > main > div.box_border.menu_top > div > div.dFlex.dIB_m.w100_m > div:nth-child(2) > div:nth-child(7) > div:nth-child(1) > div.fs14.mb10 > div > span:nth-child(2)').text
        except:
            logging.error('Contract element from Computrabajo not found')
            return None
        aux = rawOffer(title, company, description, salary,
                       education, experience, contract, date)

        return aux
    except:
        pass

# Read all the offerts main page


def webScraperComputrabajo():

    # Page initializer
    try:
        # Computrabajo URL of the last post in the last 7 days

        # Initializa the web driver
        driver = webdriver.Chrome(options=options)

        time.sleep(randomSleep())

        # List of offers
        listOffers = []

        # Iterate each offert in a page
        page = 1
        for tab in range(300):
            # Set the url, adding the page to start
            driver.get(pageURL.COMPUTRABAJO+str(page))
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
                # Get the date of the offer
                try:
                    date = box.find_element(By.CLASS_NAME, 'fc_aux').text
                    box.click()
                except Exception as e:
                    logging.error(f'Error en id: {ids[i]}\n')
                    pass
                # End the program and send the raw_offers
                if 'Ayer' in date:
                    logging.info(
                        f"Today's extraction: {len(listOffers)} offers \nPages viewed: {page}")
                    return listOffers

                # Define the element to read
                box_details = driver.find_element(
                    By.CSS_SELECTOR, 'div.box_detail')

                time.sleep(randomSleep())
                aux = Offer(box_details, date)
                if aux is not None:
                    listOffers.append(aux)

            # Click button to the next page offer
            nextButton = driver.find_element(
                By.XPATH, '/html/body/main/div[6]/div/div[2]/div[1]/div[7]/span[2]')
            nextButton.click()

            page += 1

        driver.close()

        listOffers = list(filter(None, listOffers))

        logging.info(
            f"Today's extraction: {len(listOffers)} offers \nPages viewed: {page}")

        return listOffers
    except Exception:
        driver.close()

        listOffers = list(filter(None, listOffers))

        logging.info(
            f"Today's extraction: {len(listOffers)} offers \nPages viewed: {page}")

        return listOffers