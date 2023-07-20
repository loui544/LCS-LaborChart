from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from clases import *


from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import colorama as c
import time

from clases.raw_offer import raw_offer 


#opciones de navegación 
c.init()
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')
# options.add_argument('--allow-running-insecure-content')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--log-level=3')
#options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')

tSleep1 = 1
lista_offertas = []
listaClases = []
lista_Elementos_depurados = []

#inizializar navegador 
url = 'https://www.elempleo.com/co/ofertas-empleo/bogota/hace-1-semana'
#https://www.elempleo.com/co/ofertas-empleo/bogota/hace-1-semana

driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(tSleep1)
WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div[3]/div[1]/div[3]')))




# Obtener todos los elementos <div> dentro del elemento padre utilizando el selector CSS deseado
div_elements  =  driver.find_elements(By.CSS_SELECTOR, 'div.result-item')



#Limpieza de datos
for div in div_elements:
    texto_div = div.text
    lineas = texto_div.split('\n')
    if  "EMPRESA CONFIDENCIAL" not in div.text.upper()  and "SALARIO A CONVENIR" not in div.text.upper() :
        if "Bogotá" in lineas[2]:
            lista_Elementos_depurados.append(div)
    

#esta parte del codigo nos muestra como pasar a otra pagina 
try:
   for div in lista_Elementos_depurados:
        aux = raw_offer
        texto_div = div.text
        lineas = texto_div.split('\n')
        enlace = div.find_element(By.CSS_SELECTOR, 'a.text-ellipsis.js-offer-title' )
        driver.execute_script("arguments[0].scrollIntoView();", enlace)
        enlace.send_keys(Keys.CONTROL + Keys.RETURN)
        #print(texto_div) 
        
        time.sleep(1)
        ventanas_abiertas = driver.window_handles
        driver.switch_to.window(ventanas_abiertas[1])
        time.sleep(2)
        aux = raw_offer(None, None,None, None, None, None, None,None  )
        #hacer la recolección de datos de las paginas 
        title = driver.find_element(By.CSS_SELECTOR, 'span.js-jobOffer-title')
        company = driver.find_element(By.CSS_SELECTOR, 'h2.ee-mod.ee-wrap-text.ee-offer-company-title.js-company-name')
        description = driver.find_element(By.CSS_SELECTOR, 'div.description-block')
        salary = driver.find_element(By.CSS_SELECTOR, 'span.js-joboffer-salary')
        education = driver.find_element(By.CSS_SELECTOR, 'span.js-education-level')
        #ux.experience = driver.find_element(By.CSS_SELECTOR, '')#no tienen nombre de itqueta 
        #aux.contract = driver.find_element(By.CSS_SELECTOR, '')#tampoco hay etiqueta 
        date = driver.find_element(By.CSS_SELECTOR, 'span.js-publish-date')
        #cambiar a pestaña 1 de vuelta 
        #print(title)
        texto_titulo = title.text
        texto_empresa = company.text
        texto_descripcion = description.text
        texto_salario = salary.text
        texto_educacion = education.text
        texto_fecha = date.text
        aux = raw_offer(texto_titulo, texto_empresa,texto_descripcion, texto_salario, texto_educacion, None, None,texto_fecha  )
        print(aux)
        print(texto_salario)
        print()
        print()
        driver.close()
        driver.switch_to.window(ventanas_abiertas[0]) 
        time.sleep(3)
   
   


    
except Exception as e:
    print("Error: ", e)


"""action_chains = ActionChains(driver)
action_chains.key_down(Keys.CONTROL).click(enlace).key_up(Keys.CONTROL).perform()"""
"""for pages in range(2):
    pass
driver.close()"""
