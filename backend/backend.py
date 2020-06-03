from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from flask import abort
import ssl
from model_mongodb import Diary
import data_model as model

app = Flask(__name__)
CORS(app)

diaries = []
diary1 = model.Diary("My Diary")

entry1 = model.Entry()
entry1.updateEntry("Entry 1",["first", "fun"], "This is my first Entry!!!!")

entry2 = model.Entry()
entry2.updateEntry("Entry 2",["second", "fun"], "This is my second Entry!!!!")

entry3 = model.Entry()
entry3.updateEntry("Entry 3",["third", "fun"], "This is my third Entry!!!!")

diary1.appendEntry(entry1)
diary1.appendEntry(entry2)
diary1.appendEntry(entry3)

diaries.append(diary1)





@app.route('/diaries', methods=['GET', 'POST'])
def retrieve_diaries():
    if request.method == 'GET':
        #diaries = Diary().find_all()
        #return {"diaries": diaries}, 200
        return jsonify([diary.json() for diary in diaries]), 200
    elif request.method == 'POST':
        # diaryToAdd = request.get_json()
        # newDiary = Diary(diaryToAdd)
        # newDiary.save()
        title = None
        if request.args.get("title") is not None:
            title = request.args.get("title")
        elif request.json and request.json["title"] is not None:
            title = request.json["title"]
        else:
            return jsonify(error="need to enter a title"), 400

        newDiary = model.Diary(title)
        diaries.append(newDiary)
        resp = jsonify(newDiary.__dict__), 200
        return resp

    else:
        return jsonify(error="bad request"), 400


@app.route('/diaries/<int:diaryId>', methods=['GET', 'PUT', 'DELETE'])
def retrieve_diary(diaryId):
    diary = [diary.json() for diary in diaries if diary.id == diaryId]

    if not len(diary):
        return jsonify(error=404, text="diary not found"), 404

    diary = diary[0]

    if request.method == "GET":
        return diary

    elif request.method == "PUT":
        title = request.args.get("title")

        if title:
            diary.title = title

        return jsonify(success=True)

    elif request.method == "DELETE":
        for i, d in enumerate(diaries):
            if d.id == diaryId:
                del diaries[i]

        return jsonify(success=True)

    else:
        return jsonify(error=404, text="not found"), 404

@app.route('/diaries/<int:diaryId>/entries', methods=['GET', 'PUT', 'DELETE', 'POST'])
def entries(diaryId):
    diary = [diary for diary in diaries if diary.id == diaryId]

    if not len(diary):
        return jsonify(error=404, text="diary not found"), 404

    diary = diary[0]

    if request.method == "GET":
        entries = [entry for entry in diary.entries]
        return jsonify(entries)
    elif request.method == "POST":
        title = None
        if request.args.get("title"):
            title = request.args.get("title")
        elif request.json and request.json["title"]:
            title = request.json["title"]
        else:
            return jsonify(error="Need a title to create entry"), 400

        entry = model.Entry(title)

        for d in diaries:
            if d.id == diaryId:
                d.entries.append(entry)

        return jsonify(entry.__dict__)

@app.route('/diaries/<int:diaryId>/entries/<int:entryId>', methods=['GET', 'DELETE', 'PUT'])
def modifyEntries(diaryId, entryId):
    diary = [diary for diary in diaries if diary.id == diaryId]

    if not len(diary):
        return jsonify(error=404, text="diary not found"), 404

    diary = diary[0]

    entries = diary.entries

    entry = [entry for entry in entries if entry["id"] == entryId]

    if not len(entry):
        return jsonify(error=404, text="entry not found"), 404

    entry = entry[0]

    if request.method == "GET":
        return jsonify(entry)
    elif request.method == "PUT":
        title = entry.title
        text = entry.text
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
            tags = request.args.get("tags")
        elif request.json and request.json["tags"]:
            tags = request.json["tags"]

        entry.updateEntry(title, tags, text)

        return jsonify(success=True)

    elif request.method == "DELETE":
        diary.removeEntry(entryId)

        return jsonify(success=True)





# # this needs to be done properly; still just copy pasted
# @app.route('/diaries/<id>', methods=['GET', 'DELETE'])
# def get_entries(id):
#     diary = [diary.json() for diary in diaries if diary.id == diaryId]

#     if not len(diary):
#         return jsonify(error=404, text="diary not found"), 404
#     # diary = Diary({"_id": id})
#     if request.method == "GET":
#         # diary.reload()
#         return jsonify(diary[0].entries), 200
#     if request.method == 'DELETE':
#         success = diary.remove()
#         return jsonify(success), 204  # set http response to show No Content

#         # entryToAdd = request.get_json()
#         # newEntry = Entry(entryToAdd)  # don't have an Entry class...
#         # newEntry.save()
#         # resp = jsonify(newEntry), 200
#         # return resp
