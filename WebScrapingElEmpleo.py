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
cont_ofertas = 0

#inizializar navegador 
url = 'https://www.elempleo.com/co/ofertas-empleo/bogota/hace-1-semana'
#https://www.elempleo.com/co/ofertas-empleo/bogota/hace-1-semana

driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(tSleep1)
WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div[3]/div[1]/div[3]')))

while cont_ofertas <= 400:

    # Obtener todos los elementos <div> dentro del elemento padre utilizando el selector CSS deseado
    div_elements  =  driver.find_elements(By.CSS_SELECTOR, 'div.result-item')



    #Limpieza de datos
    for div in div_elements:
        texto_div = div.text
        lineas = texto_div.split('\n')
        if  "EMPRESA CONFIDENCIAL" not in div.text.upper()  and "SALARIO A CONVENIR" not in div.text.upper() :
            if "Bogotá" in lineas[2]:
                lista_Elementos_depurados.append(div)
        

    #esta parte del codigo intera sobre la lista que sale en la pagina 
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


                #crea una pagina , y cambia a la pagina 
                ventanas_abiertas = driver.window_handles
                driver.switch_to.window(ventanas_abiertas[1])
                time.sleep(1)


                #hacer la recolección de datos de las paginas 
                aux = raw_offer(None, None,None, None, None, None, None,None  )
                title = driver.find_element(By.XPATH, '/html/body/div[7]/div[1]/div/div[1]/h1/span')
                company = driver.find_element(By.CSS_SELECTOR, 'h2.ee-mod.ee-wrap-text.ee-offer-company-title.js-company-name')
                description = driver.find_element(By.CSS_SELECTOR, 'div.description-block')
                salary = driver.find_element(By.XPATH, '/html/body/div[7]/div[1]/div/div[1]/div[2]/div[1]/p[1]/span/span[1]')
                education = driver.find_element(By.CSS_SELECTOR, 'span.js-education-level')
                experiencia = driver.find_element(By.XPATH, '/html/body/div[7]/div[2]/div[1]/div[2]/div[2]/div[2]/p[1]/span')#no tienen nombre de itqueta 
                contract = driver.find_element(By.XPATH, '/html/body/div[7]/div[2]/div[1]/div[2]/div[2]/div[2]/p[2]/span')#tampoco hay etiqueta 
                date = driver.find_element(By.CSS_SELECTOR, 'span.js-publish-date')
                
                
                #recolecta las variables y las mete en el auxilar oferta 
                texto_titulo = title.text
                texto_empresa = company.text
                texto_descripcion = description.text
                texto_descripcion_2 =texto_descripcion.replace('\n', '')
                texto_salario = salary.text
                texto_educacion = education.text
                texto_experiencia = experiencia.text
                text_contract = contract.text
                texto_fecha = date.text
                aux = raw_offer(texto_titulo, texto_empresa,texto_descripcion_2, texto_salario, texto_educacion, texto_experiencia, text_contract,texto_fecha  )
                print(aux)
                cont_ofertas = cont_ofertas + 1
                #lista_offertas.append(aux)


                #cambiar a pestaña 1 de vuelta 
                driver.close()
                driver.switch_to.window(ventanas_abiertas[0]) 
                time.sleep(1)   
    except Exception as e:
        print("Error: ", e)
    """for div in lista_offertas:
        lista_texto = div.text
        print(lista_texto)"""
driver.close()



