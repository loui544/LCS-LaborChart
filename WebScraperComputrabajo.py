from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import time
import colorama as c
import random
import os

# Add browser drivers to PATH
os.environ['PATH'] += r"C:/SeleniumDrivers"

# Read the a offer
def Offer(box_details, id):
    try:
        if 'A convenir' not in box_details.find_element(By.CSS_SELECTOR, 'span.tag base mb10'.replace(' ', '.')).text:
            title = box_details.find_element(
                By.CSS_SELECTOR, 'p.title_offer').text
            company = box_details.find_element(
                By.XPATH, 'div[1]/div[1]/a').text
            salary = box_details.find_element(
                By.CSS_SELECTOR, 'span.tag base mb10'.replace(' ', '.')).text
            description = box_details.find_element(
                By.CSS_SELECTOR, 'body > main > div.box_border.menu_top > div > div.dFlex.dIB_m.w100_m > div:nth-child(2) > div:nth-child(7) > div:nth-child(1) > div.fs16').text.replace('\n', ' ')
            requirements = box_details.find_elements(By.CSS_SELECTOR, 'li.mb5')
            print(id+'\t' + title+'\t' + company+'\t' + salary +
                  '\n' + description+'\n'+'REQUERIMIENTOS' + '\n\n')
        else:
            print(id+'\t'+"Salario no disponible\n\n")
    except:
        pass

# Read all the offerts main page
def WebScraperComputrabajo():
    c.init()

    # Initialize the driver options for the browser
    options = webdriver.ChromeOptions()

    # Open the browser window full
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--log-level=3')

    # Page initializer
    page = 1
    start = time.perf_counter()

    # Computrabajo URL of the last post in the last 7 days
    url = 'https://co.computrabajo.com/empleos-en-bogota-dc?pubdate=7&by=publicationtime&p='

    # Initializa the web driver
    driver = webdriver.Chrome(options=options)

    # Set the url, adding the page to start
    driver.get(url + str(page))
    time.sleep(random.randint(0, 2))

    # Iterate each offert in a page
    for page in range(3):
        # Get box_offer class elements
        box_offers = driver.find_elements(By.CLASS_NAME, 'box_offer')
        ids = []

        # Get the offers id of those with company name public
        for offer in box_offers:
            if 'Importante empresa' not in offer.find_element(By.CSS_SELECTOR, 'p.fs16.fc_base.mt5.mb5').text:
                ids.append(offer.get_attribute('data-id'))
        print("Empleos en pagina " + str(page) + ": " + str(len(ids)) + "\n")

        # Get info of the offer
        for i in range(len(ids)):
            # Select the offer to extract information
            box = box_offers[i]
            box.click()

            # Define the element to read
            box_details = driver.find_element(
                By.CSS_SELECTOR, 'div.box_detail')
            Offer(box_details, ids[i])

        # Click button to the next page offer
        nextButton = driver.find_element(
            By.XPATH, '/html/body/main/div[6]/div/div[2]/div[1]/div[7]/span[2]')
        nextButton.click()
        page += 1
        driver.get(url + str(page))

    driver.close()
    end = time.perf_counter()
    print("\nTiempo de ejecucion: " + str(end - start))


WebScraperComputrabajo()