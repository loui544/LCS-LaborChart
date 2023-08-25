from flask import Flask, request, jsonify, abort, make_response
from APITaggerService import tagOffers
import json
import requests

server = Flask(__name__)
 

#recibimos el json 
@server.route('/retrieveDescriptions', methods=['POST'])
def retrieveData():
    try:
        descriptions = json.dumps(request.get_json())
        result=tagOffers(descriptions)
        print(result)
        return make_response(result, 200)    
    except Exception as e:
        return make_response("JSON vacío", 400)

if __name__ == '__main__':
    server.run(debug=True, port = 5000)