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
        elif request.json and "title" in request.json is not None:
            title = request.json["title"]
        else:
            return jsonify(error="need to enter a title"), 400

        newDiary = Diary({"title": title, "entries": [], "dateCreated": datetime.datetime.utcnow()})
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

@app.route('/diaries/<diaryId>/entries', methods=['GET', 'POST'])
def entries(diaryId):
    diary = Diary().find_by_id(diaryId)

    if not len(diary):
        return jsonify(error=404, text="diary not found"), 404

    diary = diary[0]

    if request.method == "GET":
        entries = Entry().get_entries_with_diary_id(diaryId)

        if request.json and "tags" in request.json:
            tags = request.json["tags"]
            entries = Entry.filter_with_tags(entries, tags)
        if request.json and "sortBy" in request.json:
            sortBy = request.json["sortBy"].lower()
            sortBy_to_ascending = {"mostrecent": True, "leastrecent": False}

            if sortBy in sortBy_to_ascending:
                entries = Entry.sort_entries(entries, mostRecent=sortBy_to_ascending[sortBy])


        return jsonify(Entry.make_printable(entries)), 200
    elif request.method == "POST":
        title = None
        if request.args.get("title"):
            title = request.args.get("title")
        elif request.json and "title" in request.json:
            title = request.json["title"]
        else:
            return jsonify(error="Need a title to create entry"), 400

        doc = {"d_id": diaryId, "tags": [], "textBody": "",
        "dateCreated": datetime.datetime.now(), "title": title}

        entry = Entry(doc)
        entry.save()

        return jsonify(entry)

@app.route('/diaries/<diaryId>/entries/<entryId>/tags/<tag>', methods=['DELETE', 'POST'])
def modifyTags(diaryId, entryId, tag):
    print(tag)
    entry = Entry().find_by_id(entryId)

    if not len(entry):
        return jsonify(error=404, text="entry not found"), 404

    entry = Entry({"_id": entryId, "d_id": diaryId})
    entry.reload()

    if request.method == "DELETE":
        tags = entry["tags"]
        if tag not in tags:
            return jsonify(error="Tag not found"), 404
        else:
            entry["tags"].remove(tag)
            entry.save()
            return jsonify(sucess=True)
    elif request.method == "POST":
        tags = entry["tags"]

        if tag in tags:
            return jsonify(error="No duplicate tags"), 400
        else:
            entry["tags"].append(tag)
            entry.save()
            return jsonify(sucess=True)




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
        title = entry["title"]
        text = entry["textBody"]
        tags = []

        if request.args.get("title"):
            title = request.args.get("title")
        elif request.json and "title" in request.json:
            title = request.json["title"]

        if request.args.get("text"):
            text = request.args.get("text")
        elif request.json and "text" in request.json:
            text = request.json["text"]

        if request.args.get("tags"):
            return jsonify(error="Tags must be in the request body not in the params"), 400
        elif request.json and "tags" in request.json:
            tags = list(set(request.json["tags"]))

        entry["title"] = title
        entry["textBody"] = text
        entry["tags"] = tags
        entry.save()

        return jsonify(success=True)

    elif request.method == "DELETE":
        succeed = True if entry.remove() else False

        return jsonify(success=succeed)
