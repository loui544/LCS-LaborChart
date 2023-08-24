import os
import json
import numpy as np

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from transformers import AutoTokenizer, TFAutoModelForTokenClassification, pipeline
from utilis import ner_cleaning


def removeKeys(entity):
    entity.pop('index', None)
    entity.pop('start', None)
    entity.pop('end', None)
    return entity


def tagger(offersDescriptions):

    # Load Model and Instantiate Token Classification Pipeline
    checkpoint = "afrodp95/bert-base-spanish-wwm-cased-finetuned-job-skills-ner"
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = TFAutoModelForTokenClassification.from_pretrained(checkpoint)

    tokenClassifier = pipeline(
        task="token-classification",
        model=model,
        tokenizer=tokenizer,
        framework="tf",
        ignore_labels=[],
    )

    # Do NER using the pipeline
    predictedLabels = tokenClassifier(offersDescriptions)

    # Labels processing
    # n_cpus = int(multiprocessing.cpu_count()/2)
    # n_cpus = 2
    # with multiprocessing.Pool(n_cpus) as pool:
    #     labeled_entities = pool.map(ner_cleaning,predicted_labels)
    labeledEntities = [
        ner_cleaning(labels) for labels
        in predictedLabels
    ]

    # Dump labeled entities into a Json file
    result = {
        i: {
            "entities": list(map(removeKeys, entities))
        }
        for i, entities in
        enumerate(labeledEntities)
    }

    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return json.JSONEncoder.default(self, obj)

    return json.dumps(result, indent=4, cls=NpEncoder)


description1 = 'Empresa Multinacional con mas de 60 años en investigación y desarrollo de productos médicos de la más alta calidad, orientados a mejorar la calidad de vida de toda clase de pacientes a nivel global, busca talento en el área de Logística y distribución : El profesional esperado en nuestro equipo seria: 1. Profesional en Administración de empresas o Ingeniería Industrial 2. Experiencia 5 años en bodegaje / Supply Chain 3. Manejo alto de Excel 4. Conocimiento Alto ERP SAP 5. Conocimiento en Legislación Aduanera, Comercio Exterior y procesos logísticos Esperamos tu postulación a esta gran oportunidad Contrato termino indefinido mas beneficios. Palabras clave bodega supply chain sap Cargos relacionados Ingeniero industrial'
description2 = '¿Te encuentras en búsqueda de empleo?  Esta es tu oportunidad de iniciar el 2023 con un trabajo estable.  Postúlate con nosotros, aquí adquirirás experiencia en atención al cliente y habilidades para hablar en público, comunicarte de forma asertiva y trabajar en equipo.  Función: aplicación de encuestas a una población objetivo, bien sea de investigación de mercado, opinión social u opinión pública en nuestro Call Center ubicado en Bogotá-Teusaquillo cerca de la estación de Transmilenio de la Calle 34.  ¿Qué te brindamos? - Pago día laborado $45.000 pesos (L-S) y 65.000 (D y Festivos) - Crecimiento dentro de la compañía: Cambio de contrato a obra o labor dependiendo de desempeño - Disponibilidad: Completa - Beneficio en Seguridad Social - Contrato Directo con la empresa (Sin terceros)  ¿Qué requerimos? Bachilleres, técnicos, tecnólogos o profesionales mayores de edad que vivan en la ciudad de Bogotá CON EXPERIENCIA LABORAL EN VENTAS, SERVICIO AL CLIENTE, CALL CENTER O SIMILARES DE 3 MESES EN ADELANTE, con disposición y excelente actitud.  Contratación inmediata  ¡Postúlate y te contactaremos lo más pronto posible!  ¡No pierdas esta oportunidad!                       Palabras clave Encuestador Call center Servicio al cliente Encuestador Telefonico Evaluador Oficina VENTAS Cargos relacionados Encuestador telefónico Encuestador Evaluador'
descriptions = [description1, description2]
result = tagger(descriptions)
print(result)
