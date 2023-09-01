import requests
import json
from ETL.Classes.Values import *


# File where are the offers
filename = 'ETL\Extraction\offers.json'
try:
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    if data:
        # Obtener solo las descripciones de las ofertas
        descriptions = [{"description": offer['description']}
                        for offer in data]

except FileNotFoundError:
    print("El archivo no se encontró.")
except Exception as e:
    print("Error:", e)

try:
    #
    response = requests.post(uri.SkillsTaggerAPI, json=descriptions)
    #
    if response.status_code == 200:
        result = response.json()

        for idx, item in enumerate(data):
            if str(idx) in result:
                data[idx]["entities"] = result[str(idx)]["entities"]

        with open('ETL\Transformation\desc.json', 'w', encoding='utf-8') as desc_file:
            json.dump(data, desc_file, indent=4, ensure_ascii=False)
        print("Respuesta del servidor guardada en 'desc.json'")
    else:
        print("Error en la solicitud. Código de respuesta:", response.status_code)

except requests.exceptions.RequestException as e:
    print("Error en la conexión:", e)
