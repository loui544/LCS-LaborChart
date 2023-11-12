import faiss
from sentence_transformers import SentenceTransformer
from dagster import get_dagster_logger

logger = get_dagster_logger()


class faissParameters:
    CLUSTERS = 20
    CENTROIDIDS = 24
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
        logger.error(f'(LABORCHART) Error trying to train the PQ technic: {e}')
        raise ValueError(e)
