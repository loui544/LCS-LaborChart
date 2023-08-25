import requests
import json

def get_offers_with_last_date(filename):
    try:
        with open(filename, 'r',encoding='utf-8') as file:
            data = json.load(file)

        if data:
            # Ordenar las ofertas por fecha en orden descendente
            sorted_data = sorted(data, key=lambda x: x['date'], reverse=True)
            
            # Obtener la fecha de la última oferta
            last_date = sorted_data[0]['date']
            
            # Filtrar las ofertas que tienen la misma fecha que la última oferta
            offers_with_last_date = [offer for offer in sorted_data if offer['date'] == last_date]
            
            # Obtener solo las descripciones de las ofertas
            descriptions = [{"description":offer['description']} for offer in offers_with_last_date]
            
            return descriptions
        
        return []
    
    except FileNotFoundError:
        print("El archivo no se encontró.")
        return []
    except Exception as e:
        print("Error:", e)
        return []

# Nombre del archivo offers.json
filename = 'offers.json'

# Datos en formato JSON que deseas enviar al servidor
data= get_offers_with_last_date(filename)

# URL del servidor API
api_url = 'http://localhost:5000/retrieveDescriptions'

try:
    # Envía la solicitud POST con los datos JSON al servidor
    response = requests.post(api_url, json=data)
    # Verifica el código de respuesta
    if response.status_code == 200:
        result = response.json()
        with open('desc.json', 'w', encoding='utf-8') as desc_file:
            json.dump(result, desc_file, indent=4, ensure_ascii=False)
        print("Respuesta del servidor guardada en 'desc.json'")
    else:
        print("Error en la solicitud. Código de respuesta:", response.status_code)

except requests.exceptions.RequestException as e:
    print("Error en la conexión:", e)
