class pageURL:
    COMPUTRABAJO = 'https://co.computrabajo.com/empleos-en-bogota-dc?pubdate=7&by=publicationtime&p='
    ELEMPLEO = 'https://www.elempleo.com/co/ofertas-empleo/bogota/hace-1-semana'


class rabbitQueue:
    COMPUTRABAJO = 'computrabajo'
    ELEMPLEO = 'elempleo'
    QUEUES = [COMPUTRABAJO, ELEMPLEO]


class url:
    CTDRIVER = 'http://ctdriver:4444/wd/hub'
    EEDRIVER = 'http://eedriver:4444/wd/hub'
    SKILLSTAGGERAPI = 'http://apitagger:5000/retrieveDescriptions'
    ELASTICSEARCH = 'http://elasticsearch:9200'
    RABBITMQ = 'rabbitmq'


class elasticSearch:
    INDEX = 'laborchart'
