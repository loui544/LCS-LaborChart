import re


class rawOffer:
    def __init__(self, title, company, description, salary, education, experience, contract, date):
        self.title = title
        self.company = company
        self.description = description
        self.salary = salary
        self.education = education
        self.experience = experience
        self.contract = contract
        self.date = date

    def lowerCase(self):
        self.title = re.sub(
            '[^a-zA-Z0-9 áéíóúÁÉÍÓÚüñ \n\.]', '', self.title.lower().replace('\n', ' ').replace('.', ''))
        self.company = re.sub(
            '[^a-zA-Z0-9 áéíóúÁÉÍÓÚüñ \n\.]', '', self.company.lower().replace('\n', ' ').replace('.', ''))
        self.description = re.sub(
            '[^a-zA-Z0-9 áéíóúÁÉÍÓÚüñ \n\.]', '', self.description.lower().replace('\n', ' ').replace('.', ''))

    def __str__(self):
        return 'Nombre: {0}\nEmpresa: {1}\nDescripcción: {2}\nSalario: {3}\nNivel educativo: {4}\nExperiencia requerida: {5}\nTipo de contrato: {6}\nFecha de publicación: {7}\n'.format(self.title, self.company, self.description, self.salary, self.education, self.experience, self.contract, self.date)
