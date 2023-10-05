import faiss
from sentence_transformers import SentenceTransformer
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    filename='Logs/'+datetime.today().strftime('%d-%m-%Y')+'.log'
)


class faissParameters:
    CLUSTERS = 10
    CENTROIDIDS = 8
    SEARCHSCOPE = 5
    NEAREST = 5


def centroidBits(offersLen, max=8):
    if offersLen <= 1:
        return 0
    else:
        exponent = (offersLen - 1).bit_length() - 1
        return min(exponent, max)


def modelTraining(titlesCompanies):
    try:
        # Encoding title-company list
        model = SentenceTransformer('bert-base-nli-mean-tokens')
        offersEmbeddings = model.encode(
            titlesCompanies, show_progress_bar=False)

        # setting parameters for Product Quantization model
        vectorsDimensionality = offersEmbeddings.shape[1]
        quantizier = faiss.IndexFlatL2(vectorsDimensionality)
        index = faiss.IndexIVFPQ(quantizier, vectorsDimensionality, faissParameters.CLUSTERS,
                                 faissParameters.CENTROIDIDS, centroidBits(len(titlesCompanies)))

        # Training and preparing model for production
        index.train(offersEmbeddings)
        index.add(offersEmbeddings)
        index.nprobe = faissParameters.SEARCHSCOPE

        return model, index
    except Exception as e:
        logging.error(f'Error trying to train the PQ technic: {e}')
