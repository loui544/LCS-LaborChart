# LCS-LaborChart

Laborchart es un sistema que permite visualizar las tendencias de la demanda de habilidades en el mercado laboral de Bogotá, mediante un dashboard. Además, es periódicamente alimentado por un flujo de datos que, por medio de Web Scraping, extrae datos relevantes de ofertas publicadas por empresas. Además, procesa y normaliza estos datos, y muy importante, hace uso de un modelo de etiquetadio de habilidades (MEH). Este modelo identifica las habilidades que son demandadas en las descripcione de las ofertas, por medio de ténicas de procesamiento de lenguaje natural (NLP), y las categoriza en tres competencias: socioemocional, técnico, o digital.

# Requisitos
Para ejecutar el sistema es necesario los siguientes requisitos:
- Docker
- Docker Compose

# Instruciones
- Sobre la raiz del proyecto ejecutar: docker-compose -f laborchart/docker-compose.yaml up
- Esperar que el servicio se esté ejecutando completamente
- Ejecutar: docker-compose -f apitagger/docker-compose.yaml up

Ahora puedes hacer uso de LaborChart.

# Recomendación
Ejecutar en mínimo en una máquina con mínimo: CPU de 8 cores, memoria 16GB, y almacenamiento de 16GB (almacenamiento alojado para los contenedores)

# ¡Advertencia!!
No eliminar el folder "volumes".
