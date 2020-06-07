from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from flask import abort
import ssl
from model_mongodb import *
import data_model as model
import datetime

app = Flask(__name__)
CORS(app)

@app.route('/diaries', methods=['GET', 'POST'])
def retrieve_diaries():
    if request.method == 'GET':
        diaries = Diary().get_all_diaries()
        return {"diaries": diaries}, 200
    elif request.method == 'POST':
        if request.args.get("title") is not None:
            title = request.args.get("title")
        elif request.json and request.json["title"] is not None:
            title = request.json["title"]
        else:
            return jsonify(error="need to enter a title"), 400

        newDiary = Diary({"title": title, "dateCreated": datetime.datetime.now(),
           "entries": []})
        newDiary.save()
        resp = jsonify(newDiary.make_printable(newDiary)), 200
        return resp
    else:
        return jsonify(error="bad request"), 400


@app.route('/diaries/<diaryId>', methods=['GET', 'PUT', 'DELETE'])
def retrieve_diary(diaryId):
    diary = Diary().find_by_id(diaryId)

    if not len(diary):
        return jsonify(error=404, text="diary not found"), 404

    diary = Diary(diary[0])

    if request.method == "GET":
        diary["entries"] = Entry().get_entries_with_diary_id(diaryId)
        return jsonify(Diary().make_printable(diary))

    elif request.method == "PUT":
        title = request.args.get("title")

        if title:
            diary["title"] = title
            diary.save()

        return jsonify(success=True)

    elif request.method == "DELETE":
        diary.remove()

        return jsonify(success=True)

    else:
        return jsonify(error=404, text="not found"), 404

@app.route('/diaries/<diaryId>/entries', methods=['GET', 'PUT', 'DELETE', 'POST'])
def entries(diaryId):
    diary = Diary().find_by_id(diaryId)

    if not len(diary):
        return jsonify(error=404, text="diary not found"), 404

    diary = diary[0]

    if request.method == "GET":
        entries = Entry().get_entries_with_diary_id(diaryId)
        return jsonify(Entry.make_printable(entries)), 200
    elif request.method == "POST":
        title = None
        if request.args.get("title"):
            title = request.args.get("title")
        elif request.json and request.json["title"]:
            title = request.json["title"]
        else:
            return jsonify(error="Need a title to create entry"), 400

        doc = {"d_id": diaryId, "tags": [], "textBody": "",
           "title": title}

        entry = Entry(doc)
        entry.save()

        return jsonify(entry)

@app.route('/diaries/<diaryId>/entries/<entryId>', methods=['GET', 'DELETE', 'PUT'])
def modifyEntries(diaryId, entryId):
    entry = Entry().find_by_id(entryId)

    if not len(entry):
        return jsonify(error=404, text="entry not found"), 404

    entry = Entry({"_id": entryId, "d_id": diaryId})
    entry.reload()

    if request.method == "GET":
        return jsonify(entry)
    elif request.method == "PUT":
        entryObj = Entry({"_id": entryId, "d_id": diaryId})
        entryObj.reload()

        title = entry["title"]
        text = entry["textBody"]
        tags = []

        if request.args.get("title"):
            title = request.args.get("title")
        elif request.json and request.json["title"]:
            title = request.json["title"]

        if request.args.get("text"):
            text = request.args.get("text")
        elif request.json and request.json["text"]:
            text = request.json["text"]

        if request.args.get("tags"):
            return jsonify(error="Tags must be in the request body not in the params"), 400
        elif request.json and request.json["tags"]:
            tags = list(set(request.json["tags"]))

        entryObj["title"] = title
        entryObj["textBody"] = text
        entryObj["tags"] = tags
        entryObj.save()

        return jsonify(success=True)

    elif request.method == "DELETE":
        succeed = True if entry.remove() else False

        return jsonify(success=succeed)
