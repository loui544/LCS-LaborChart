import json
import numpy as np
from transformers import AutoTokenizer, TFAutoModelForTokenClassification, pipeline
from skillstagger.utilis import ner_cleaning


def removeKeys(entity):
    entity.pop('index', None)
    entity.pop('start', None)
    entity.pop('end', None)
    return entity


def descriptionsResult(offersDescriptions):

    # Load Model and Instantiate Token Classification Pipeline
    checkpoint = "afrodp95/bert-base-spanish-wwm-cased-finetuned-job-skills-ner"
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = TFAutoModelForTokenClassification.from_pretrained(checkpoint)

    tokenClassifier = pipeline(
        task="token-classification",
        model=model,
        tokenizer=tokenizer,
        framework="tf",
        ignore_labels=[],
    )

    # Do NER using the pipeline
    predictedLabels = tokenClassifier(offersDescriptions)

    # Labels processing
    # n_cpus = int(multiprocessing.cpu_count()/2)
    # n_cpus = 2
    # with multiprocessing.Pool(n_cpus) as pool:
    #     labeled_entities = pool.map(ner_cleaning,predicted_labels)
    labeledEntities = [
        ner_cleaning(labels) for labels
        in predictedLabels
    ]

    # Dump labeled entities into a Json file
    result = {
        i: {
            "entities": list(map(removeKeys, entities))
        }
        for i, entities in
        enumerate(labeledEntities)
    }

    return result
