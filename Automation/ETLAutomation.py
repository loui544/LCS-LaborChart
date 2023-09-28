from ETL.Extraction.ElEmpleoExtraction.WebScraperElEmpleo import webScraperElempleo
from ETL.Extraction.ElEmpleoExtraction.NormalizerElEmpleo import offersNormalizer as eNormalizer
from ETL.Extraction.CompuTrabajoExtraction.WebScraperComputrabajo import webScraperComputrabajo
from ETL.Extraction.CompuTrabajoExtraction.NormalizerComputrabajo import offersNormalizer as cNormalizer
from ETL.Transformation.Receptor import reception
from ETL.Transformation.Filter import filterOffers
from ETL.Transformation.APITaggerClient import client
from ETL.Transformation.DBConnector import sendToElasticSearch
from ETL.Transformation.OffersCheck import offersCheck
from dagster import asset, define_asset_job, Definitions, schedule, RunRequest
from datetime import datetime


@asset
def elempleoExtraction() -> None:
    try:
        offers = webScraperElempleo()
        eNormalizer(offers)
    except Exception as e:
        print(e)


@asset
def computrabajoExtraction() -> None:
    try:
        offers = webScraperComputrabajo()
        cNormalizer(offers)
    except Exception as e:
        print(e)


@asset(deps=[elempleoExtraction, computrabajoExtraction])
def receptor():
    try:
        return reception()
    except Exception as e:
        print(e)


@asset
def filter(receptor):
    try:
        return filterOffers(receptor)
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


@asset(deps=[elasticConnector])
def offersSimilarityCheck() -> None:
    try:
        offersCheck()
    except Exception as e:
        print(e)


allAssetsJob = define_asset_job(name='LaborChartETL')


@schedule(job=allAssetsJob, cron_schedule='@daily', execution_timezone='America/Bogota')
def etlSchedule():
    return RunRequest(run_key=None, tags={'date': datetime.now().strftime('%d-%m-%Y %H:%M:%S')}, job_name=allAssetsJob.name)


defs = Definitions(assets=[elempleoExtraction, computrabajoExtraction, receptor, filter, apiClient, elasticConnector, offersSimilarityCheck],
                   schedules=[etlSchedule],
                   jobs=[allAssetsJob])
