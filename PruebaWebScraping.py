from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import colorama as c

c.init()
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')
# options.add_argument('--allow-running-insecure-content')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--log-level=3')

page = 1
url = 'https://co.computrabajo.com/empleos-en-bogota-dc?pubdate=7&p='
driver = webdriver.Chrome(options=options)
driver.get(url + str(page))
driver.implicitly_wait(1)
for pages in range(2):
    box_offers = driver.find_elements(By.CSS_SELECTOR, 'article.box_offer')
    ids = []
    for offer in box_offers:
        ids.append(offer.get_attribute('data-id'))
    for i in range(len(ids)):
        driver.get(url + str(page) + '#' + ids[i])
        driver.get(url + str(page) + '#' + ids[i])
        driver.implicitly_wait(1)
        WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, '/html/body/main/div[6]/div/div[2]/div[2]/div[2]/a')))
        box_details = driver.find_element(By.CSS_SELECTOR, 'div.box_detail')
        try:
            title = box_details.find_element(By.XPATH, '/html/body/main/div[6]/div/div[2]/div[2]/p').text
            company = box_details.find_element(By.XPATH, '/html/body/main/div[6]/div/div[2]/div[2]/div[1]/div[1]/div/a').text
            salary = box_details.find_element(By.CSS_SELECTOR, 'span.tag base mb10'.replace(' ', '.')).text
            description = box_details.find_element(By.CSS_SELECTOR, 'body > main > div.box_border.menu_top > div > div.dFlex.dIB_m.w100_m > div:nth-child(2) > div:nth-child(5) > div:nth-child(1) > div.fs16').text.replace('\n', ' ')
            requirements = box_details.find_elements(By.CSS_SELECTOR, 'li.mb5')
            print(c.Fore.GREEN + title + c.Fore.RESET)
            print(c.Fore.GREEN + 'Empresa: ' + c.Fore.RESET + company)
            print(c.Fore.GREEN + 'Salario: ' + c.Fore.RESET + salary.replace('(Mensual)', ''))
            print(c.Fore.GREEN + 'Descripcion: ' + c.Fore.RESET + description)
            print(c.Fore.GREEN + 'Nivel educativo mínimo: ' + c.Fore.RESET + requirements[0].text.replace('Educación mínima: ', ''))
            print(c.Fore.GREEN + 'Experiencia: ' + c.Fore.RESET + requirements[1].text.replace(' de experiencia', '') + '\n')
        except:
            print('\n')
            continue
    page += 1
    driver.get(url + str(page))
driver.close()
