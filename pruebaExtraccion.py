from ETL.Extraction.ElEmpleoExtraction.WebScraperElEmpleo import webScraperElempleo
from ETL.Extraction.ElEmpleoExtraction.NormalizerElEmpleo import offersNormalizer


offersNormalizer(webScraperElempleo())
