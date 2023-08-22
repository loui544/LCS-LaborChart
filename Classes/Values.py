class url:
    COMPUTRABAJO = 'https://co.computrabajo.com/empleos-en-bogota-dc?pubdate=7&by=publicationtime&p='
    ELEMPLEO = 'https://www.elempleo.com/co/ofertas-empleo/bogota/hace-1-semana'


class queue:
    COMPUTRABAJO = 'computrabajo'
    ELEMPLEO = 'elempleo'
    QUEUES = [COMPUTRABAJO, ELEMPLEO]


class uri:
    RABBITMQ = 'localhost'
    MONGODB = 'mongodb://localhost:27017'


class mongoDB:
    LABORCHART = 'LaborChart'


class mongoCollection:
    OFFERS = 'Offers'


class times:
    MIN = 2
    MAX = 4
