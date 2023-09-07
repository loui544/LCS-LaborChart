class pageURL:
    COMPUTRABAJO = 'https://co.computrabajo.com/empleos-en-bogota-dc?pubdate=7&by=publicationtime&p='
    ELEMPLEO = 'https://www.elempleo.com/co/ofertas-empleo/bogota/hace-1-semana'


class rabbitQueue:
    COMPUTRABAJO = 'computrabajo'
    ELEMPLEO = 'elempleo'
    QUEUES = [COMPUTRABAJO, ELEMPLEO]


class uri:
    SkillsTaggerAPI = 'http://localhost:5000/retrieveDescriptions'
    ElasticSearch = 'http://localhost:9200'
    RABBITMQ = 'localhost'
    MONGODB = 'mongodb://localhost:27017'


class mongoDB:
    DataBase = 'LaborChart'
    Collection = 'Offers'
