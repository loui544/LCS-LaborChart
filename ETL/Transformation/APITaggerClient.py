import requests
import json
from ETL.Classes.Values import *
from ETL.Config import *


def Client(offers):

    try:
        offers = json.loads(offers)
        descriptions = [{"description": offer['description']}
                        for offer in offers]
        #
        response = requests.post(uri.SkillsTaggerAPI, json=descriptions)
        #
        if response.status_code == 200:

            result = response.json()

            # Removes 'index','start',and 'end' keys
            def removeKeys(x): return {'entities': [{k: v for k, v in entity.items() if k not in [
                'index', 'start', 'end']} for entity in x['entities']]}
            result = {k: removeKeys(v)
                      for k, v in result.items()}

            for idx, item in enumerate(offers):
                if str(idx) in result:
                    item["entities"] = result[str(idx)]["entities"]

            return offers
            # with open('ETL\Transformation\desc.json', 'w', encoding='utf-8') as desc_file:
            #    json.dump(offers, desc_file, indent=4, ensure_ascii=False)
            # print("Respuesta del servidor guardada en 'desc.json'")
        else:
            raise ValueError("Error en la solicitud. Código de respuesta: ",
                             response.status_code)
    except requests.exceptions.RequestException as e:
        raise ("Error en la conexión:", e)


# filename = 'ETL\Extraction\offers.json'
# try:
#    with open(filename, 'r', encoding='utf-8') as file:
#        offers = json.load(file)
# except FileNotFoundError:
#    print("El archivo no se encontró.")
# except Exception as e:
#    print("Error:", e)
#
# Client(offers)
