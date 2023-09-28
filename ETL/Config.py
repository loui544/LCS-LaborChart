class pageURL:
    COMPUTRABAJO = 'https://co.computrabajo.com/empleos-en-bogota-dc?pubdate=7&by=publicationtime&p='
    ELEMPLEO = 'https://www.elempleo.com/co/ofertas-empleo/bogota/hace-1-semana'


class rabbitQueue:
    COMPUTRABAJO = 'computrabajo'
    ELEMPLEO = 'elempleo'
    QUEUES = [COMPUTRABAJO, ELEMPLEO]


class url:
    SKILLSTAGGERAPI = 'http://localhost:5000/retrieveDescriptions'
    ELASTICSEARCH = 'http://localhost:9200'
    RABBITMQ = 'localhost'


class elasticSearch:
    INDEX = 'laborchart'
