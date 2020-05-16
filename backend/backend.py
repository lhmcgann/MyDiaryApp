from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
import ssl
from model_mongodb import Entry

app = Flask(__name__)
CORS(app)


@app.route('/entries', methods=['GET', 'POST', 'DELETE'])
def get_entries():
    if request.method == "GET":
        entries = Entry().find_all()
        return {"entries": entries}, 200
    if request.method == 'POST':
        entryToAdd = request.get_json()
        newEntry = Entry(entryToAdd)
        newEntry.save()
        resp = jsonify(newEntry), 200
        return resp
    if request.method == "DELETE":
    	Entry().delete_all()