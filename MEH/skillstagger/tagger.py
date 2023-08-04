import os
import json
import numpy as np

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from transformers import AutoTokenizer, TFAutoModelForTokenClassification, pipeline
from utilis import ner_cleaning


## Parse command line parameters
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", type=str, help="Path to .txt files with multiple job descriptions")
parser.add_argument("-o", "--output",type=str, help="Path to json file with labeled texts")
args = vars(parser.parse_args())


## If neither text or file where provided raise error and exit
if not args['file']:
    raise ValueError("A .txt file must be provided")

## Set default filename if no output is provided
if not args['output']:
    input_filename = os.path.basename(args['file']).split('.')[0]
    input_basepath = os.path.dirname(args['file'])
    otuput_filename = os.path.join(input_basepath,f"{input_filename}_tagged.json") 
elif ".json" not in args['output']:
    input_filename = os.path.basename(args['output']).split('.')[0]
    input_basepath = os.path.dirname(args['output'])
    otuput_filename = os.path.join(input_basepath,f"{input_filename}.json") 

## Read .txt file
with open(args['file'],"r") as file:
    job_descriptions = file.readlines()


## Load Model and Instantiate Token Classification Pipeline
checkpoint = "afrodp95/bert-base-spanish-wwm-cased-finetuned-job-skills-ner"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = TFAutoModelForTokenClassification.from_pretrained(checkpoint)

token_classifier = pipeline(
    task="token-classification",
    model=model,
    tokenizer=tokenizer,
    framework="tf",
    ignore_labels=[],
)

## Do NER using the pipeline
predicted_labels = token_classifier(job_descriptions)

## Labels processing
#n_cpus = int(multiprocessing.cpu_count()/2)
# n_cpus = 2
# with multiprocessing.Pool(n_cpus) as pool:
#     labeled_entities = pool.map(ner_cleaning,predicted_labels)

labeled_entities = [
    ner_cleaning(labels) for labels
    in predicted_labels
]

## Dump labeled entities into a Json file
result = {
    i:{
        "text":text,
        "entities":entities
    } 
    for i,(text,entities) in 
    enumerate(zip(job_descriptions,labeled_entities))
}

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

with open(otuput_filename,"w") as output_file:
    json.dump(result,output_file,indent=4,cls=NpEncoder)