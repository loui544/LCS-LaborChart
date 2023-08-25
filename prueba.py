import WebScraperComputrabajo
import NormalizerComputrabajo
import time
import datetime

start_time = datetime.datetime.now()


offers=WebScraperComputrabajo.WebScraperComputrabajo()
NormalizerComputrabajo.OffersCleaning(offers)

end_time = datetime.datetime.now()
execution_time = (end_time - start_time)/60

print(f"El tiempo de ejecución fue de {execution_time.total_seconds():.4f} minutos")
print(f"Comenzó en: {start_time}")
print(f"Terminó en: {end_time}")