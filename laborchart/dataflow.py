from etl.extraction.elempleo.webscraper import webScraperElempleo
from etl.extraction.elempleo.normalizer import offersNormalizer as eNormalizer
from etl.extraction.computrabajo.webscraper import webScraperComputrabajo
from etl.extraction.computrabajo.normalizer import offersNormalizer as cNormalizer
from etl.transformation.receptor import reception
from etl.transformation.filter import filterOffers
from etl.transformation.apiconsumer import client
from etl.transformation.dbconnector import sendToElasticSearch
from etl.transformation.offersmanager import offersCheck
from dagster import asset, define_asset_job, Definitions, schedule, RunRequest, Failure
from datetime import datetime


@asset
def elempleoExtraction() -> None:
    try:
        offers = webScraperElempleo()
        eNormalizer(offers)
    except Exception as e:
        raise Failure(description=f'elempleoExtraction asset error: {e}')


@asset
def computrabajoExtraction() -> None:
    try:
        offers = webScraperComputrabajo()
        cNormalizer(offers)
    except Exception as e:
        raise Failure(description=f'computrabajoExtraction asset error: {e}')


@asset(deps=[elempleoExtraction, computrabajoExtraction])
def receptor():
    try:
        return reception()
    except Exception as e:
        raise Failure(description=f'receptor asset error: {e}')


@asset
def filter(receptor):
    try:
        return filterOffers(receptor)
    except Exception as e:
        raise Failure(description=f'filter asset error: {e}')


@asset
def apiClient(filter):
    try:
        return client(filter)
    except Exception as e:
        raise Failure(description=f'apiClient asset error: {e}')


@asset
def elasticConnector(apiClient) -> None:
    try:
        sendToElasticSearch(apiClient)
    except Exception as e:
        raise Failure(description=f'elasticConnector asset error: {e}')


@asset(deps=[elasticConnector])
def offersSimilarityCheck() -> None:
    try:
        offersCheck()
    except Exception as e:
        raise Failure(description=f'offersSimilarityCheck asset error: {e}')


allAssetsJob = define_asset_job(name='LaborChartETL')


@schedule(job=allAssetsJob, cron_schedule='@daily', execution_timezone='America/Bogota')
def etlSchedule():
    return RunRequest(run_key=None, tags={'date': datetime.now().strftime('%d-%m-%Y %H:%M:%S')}, job_name=allAssetsJob.name)


defs = Definitions(assets=[elempleoExtraction, computrabajoExtraction, receptor, filter, apiClient, elasticConnector, offersSimilarityCheck],
                   schedules=[etlSchedule],
                   jobs=[allAssetsJob])
