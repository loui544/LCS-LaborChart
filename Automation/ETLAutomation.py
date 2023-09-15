from ETL.Extraction.ElEmpleoExtraction.WebScraperElEmpleo import webScraperElempleo
from ETL.Extraction.ElEmpleoExtraction.NormalizerElEmpleo import offersNormalizer as eNormalizer
from ETL.Extraction.CompuTrabajoExtraction.WebScraperComputrabajo import webScraperComputrabajo
from ETL.Extraction.CompuTrabajoExtraction.NormalizerComputrabajo import offersNormalizer as cNormalizer
from ETL.Transformation.Receptor import reception
from ETL.Transformation.Filter import filterOffers
from ETL.Transformation.APITaggerClient import client
from ETL.Transformation.DBConnector import sendToElasticSearch
from dagster import asset
import pprint


@asset
def elempleoExtraction() -> None:
    try:
        offers = webScraperElempleo()
        eNormalizer(offers)
    except Exception as e:
        print(e)


@asset(deps=[elempleoExtraction])
def receptor() -> None:
    try:
        reception()
    except Exception as e:
        print(e)


@asset(deps=[receptor])
def filter():
    try:
        return filterOffers()
    except Exception as e:
        print(e)


@asset
def apiClient(filter):
    try:
        return client(filter)
    except Exception as e:
        print(e)


@asset
def elasticConnector(apiClient) -> None:
    try:
        sendToElasticSearch(apiClient)
    except Exception as e:
        print(e)
