from enum import Enum


class educationLevel(Enum):
    HIGH = 'Bachillerato'
    TECHNIC = 'Técnico'
    TECHNOLOGY = 'Tecnológica'
    PRE = 'Profesional Pregrado'
    SPEC = 'Profesional Especialización'
    MASTER = 'Profesional Maestría'


class contractType(Enum):
    DEF = 'Definido'
    INDEF = 'Indefinido'
    OBR = 'Por obra'
    PRES = 'Prestación de servicios'
