from flask import Flask, request, make_response
from apitaggerservice import tagOffers
import json

server = Flask(__name__)


# recibimos el json
@server.route('/retrieveDescriptions', methods=['POST'])
def retrieveData():
    """
    Retrieves data from a JSON request, processes it using the `tagOffers` function,
    and returns the result in a Flask response.

    Returns:
        flask.Response: A Flask response containing the result of processing the JSON data.
            If successful, the response code is 200; otherwise, it's 400 with an error message.
    """
    try:
        descriptions = json.dumps(request.get_json())
        result = tagOffers(descriptions)
        return make_response(result, 200)
    except Exception as e:
        return make_response("JSON vacío", 400)


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=5000)
