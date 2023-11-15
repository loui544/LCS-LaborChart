from skillstagger.tagger import descriptionsResult
import numpy as np
import json


def tagOffers(descriptions):
    """
    Processes a list of item descriptions and generates results using the `descriptionsResult` function.

    Args:
        descriptions (str): A JSON-encoded string containing a list of items with descriptions.

    Returns:
        str: A JSON-encoded string containing the results of processing the item descriptions.
    """
    descriptions = json.loads(descriptions)
    descriptions = list(map(lambda item: item['description'], descriptions))
    result = descriptionsResult(descriptions)

    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return json.JSONEncoder.default(self, obj)

    return json.dumps(result, indent=4, cls=NpEncoder)
