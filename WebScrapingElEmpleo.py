from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from clases import *

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import colorama as c
import time 


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

listaClases = []
lista_Elementos_depurados = []

#inizializar navegador 
url = 'https://www.elempleo.com/co/ofertas-empleo/hace-1-semana?trabajo=Bogota'

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

#ya vamos a trabajar sobre la lista de los empleos validos 
for div in lista_Elementos_depurados:
    texto_div = div.text    
      

    


#esta parte del codigo nos muestra como pasar a otra pagina 
try:
   for div in lista_Elementos_depurados:
        texto_div = div.text
        lineas = texto_div.split('\n')
        enlace = div.find_element(By.CSS_SELECTOR, 'a.text-ellipsis.js-offer-title' )
        driver.execute_script("arguments[0].scrollIntoView();", enlace)
        enlace.send_keys(Keys.CONTROL + Keys.RETURN)
        print(texto_div) 
        
        time.sleep(tSleep1)
        ventanas_abiertas = driver.window_handles
        driver.switch_to.window(ventanas_abiertas[1])
        time.sleep(1)
        
        #hacer la recolección de datos de las paginas 
            
   
        #cambiar a pestaña 1 de vuelta 
        driver.close()
        driver.switch_to.window(ventanas_abiertas[0]) 
        time.sleep(1)
   
   


    
except Exception as e:
    print("Error: ", e)


"""action_chains = ActionChains(driver)
action_chains.key_down(Keys.CONTROL).click(enlace).key_up(Keys.CONTROL).perform()"""
"""for pages in range(2):
    pass
driver.close()"""
