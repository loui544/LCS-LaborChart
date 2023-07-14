from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import time
import colorama as c
import random


def WebScraperComputrabajo():
    c.init()
    options = webdriver.FirefoxOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--log-level=3')

    page = 1
    inicio = time.perf_counter()
    url = 'https://co.computrabajo.com/empleos-en-bogota-dc?pubdate=7&by=publicationtime&p='
    driver = webdriver.Firefox(options=options)
    driver.get(url + str(page))
    time.sleep(random.random(0, 2))
    for pages in range(1):
        box_offers = driver.find_elements(By.XPATH, 'article.box_offer')
        ids = []
        for offer in box_offers:
            if 'Importante empresa' not in offer.find_element(By.CSS_SELECTOR, 'p.fs16.fc_base.mt5.mb5').text:
                ids.append(offer.get_attribute('data-id'))
        print("Empleos en pagina " + str(page) + ": " + str(len(ids)) + "\n")
        for i in range(len(ids)):
            driver.get(url + str(page) + '#' + ids[i])
            time.sleep(0.5)
            driver.get(url + str(page) + '#' + ids[i])
            time.sleep(0.5)
            WebDriverWait(driver, 5).until(ec.presence_of_element_located(
                (By.XPATH, '/html/body/main/div[6]/div/div[2]/div[2]/div[2]/a')))
            box_details = driver.find_element(
                By.CSS_SELECTOR, 'div.box_detail')
            try:
                if 'Salario a convenir' not in box_details.find_element(By.CSS_SELECTOR, 'span.tag base mb10'.replace(' ', '.')).text:
                    title = box_details.find_element(
                        By.XPATH, '/html/body/main/div[6]/div/div[2]/div[2]/p').text
                    print(c.Fore.GREEN + title + c.Fore.RESET)
                    company = box_details.find_element(
                        By.XPATH, '/html/body/main/div[6]/div/div[2]/div[2]/div[1]/div[1]/div/a').text
                    print(c.Fore.GREEN + 'Empresa: ' + c.Fore.RESET + company)
                    salary = box_details.find_element(
                        By.CSS_SELECTOR, 'span.tag base mb10'.replace(' ', '.')).text
                    print(c.Fore.GREEN + 'Salario: ' + c.Fore.RESET +
                          salary.replace('(Mensual)', ''))
                    description = box_details.find_element(
                        By.CSS_SELECTOR, 'body > main > div.box_border.menu_top > div > div.dFlex.dIB_m.w100_m > div:nth-child(2) > div:nth-child(7) > div:nth-child(1) > div.fs16').text.replace('\n', ' ')
                    print(c.Fore.GREEN + 'Descripcion: ' +
                          c.Fore.RESET + description)
                    requirements = box_details.find_elements(
                        By.CSS_SELECTOR, 'li.mb5')
                    print("Requirements len: " + str(len(requirements)))
                    print(c.Fore.GREEN + 'Nivel educativo mínimo: ' + c.Fore.RESET +
                          requirements[0].text.replace('Educación mínima: ', ''))
                    print(c.Fore.GREEN + 'Experiencia: ' + c.Fore.RESET +
                          requirements[1].text.replace(' de experiencia', '') + '\n')
            except:
                print('\n')
                continue
        page += 1
        driver.get(url + str(page))
    driver.close()
    final = time.perf_counter()
    print("\nTiempo de ejecucion: " + str(final - inicio))


WebScraperComputrabajo()
