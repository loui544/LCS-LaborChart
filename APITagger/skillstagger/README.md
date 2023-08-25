# Instrucciones de uso

## 1. Instalar conda para gestión de ambiente

Instalar miniconda / anaconda (como gestor de ambientes de python), conda instala su propio interprete de Python, por lo que no es requerido instalar el intérprete disponible en la página python.org. No importa que la versión base de Python que trae el instalador de conda no sea la misma que se va a usar con el script. Luego se creará un ambiente con la versión requerida.

- Miniconda:

Versión light de conda, no instala IDE ni paquete de librerías para ciencia de datos. Las librerías y ambientes las construyen según necesidad.

https://docs.conda.io/en/latest/miniconda.html

- Anaconda.

Instala IDE (Spyder) y paquete de librerías de ciencia de datos.

https://www.anaconda.com/download/

## 2. Crear el ambiente

Usar el archivo requirements.txt para crear el ambiente de python

```console
conda create --name skillsner --file requirements.txt
```

## 3. Activar el ambiente y ejecutar el script

Para activar el ambiente recientemente instalado 

```console
conda activate skillsner
```
El script de python toma como input un archivo .txt en el cual cada linea del archivo es una descripción de oferta laboral, retorna un archivo .json con las habilidades identificadas para cada una de las ofertas laborales a analizar.

```console
python tagger.py -f job_descriptions.txt -o job_descriptions_tagged.json
```

El único parámetro obligatorio es el archivo de texto a analizar, si un archivo de salida o una ruta a un archivo de salida no es proporcionada el script construirá un nombre para el archivo de salida y lo guardará en la misma ruta del archivo de entrada. Para obtener ayuda sobre los parámetros pueden usar

```console
python tagger.py -h
```



