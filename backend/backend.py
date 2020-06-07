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

# diaries = []
# diary1 = model.Diary("My Diary")

# entry1 = model.Entry()
# entry1.updateEntry("Entry 1",["first", "fun"], "This is my first Entry!!!!")

# entry2 = model.Entry()
# entry2.updateEntry("Entry 2",["second", "fun"], "This is my second Entry!!!!")

# entry3 = model.Entry()
# entry3.updateEntry("Entry 3",["third", "fun"], "This is my third Entry!!!!")

# diary1.appendEntry(entry1)
# diary1.appendEntry(entry2)
# diary1.appendEntry(entry3)

# diaries.append(diary1)





@app.route('/diaries', methods=['GET', 'POST'])
def retrieve_diaries():
    if request.method == 'GET':
        diaries = Diary().find_all()
        return {"diaries": diaries}, 200
        # return jsonify([diary.json() for diary in diaries]), 200
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

        newDiary = Diary({"title": title, "dateCreated": datetime.datetime.now(),
           "entries": []})
        newDiary.save()
        resp = jsonify(newDiary.make_printable(newDiary)), 200
        return resp
        # newDiary = model.Diary(title)
        # diaries.append(newDiary)
        # resp = jsonify(newDiary.__dict__), 200
        # return resp

    else:
        return jsonify(error="bad request"), 400


@app.route('/diaries/<diaryId>', methods=['GET', 'PUT', 'DELETE'])
def retrieve_diary(diaryId):
    # diary = [diary.json() for diary in diaries if diary.id == diaryId]

    diary = Diary().find_by_id(diaryId)

    if not len(diary):
        return jsonify(error=404, text="diary not found"), 404

    diary = Diary(diary[0])

    if request.method == "GET":
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
    # diary = [diary for diary in diaries if diary.id == diaryId]

    diary = Diary().find_by_id(diaryId)

    if not len(diary):
        return jsonify(error=404, text="diary not found"), 404

    diary = diary[0]

    if request.method == "GET":
        # entries = [entry for entry in diary.entries]
        # return jsonify(entries)
        entries = Entry({"d_id": diaryId}).get_entries()
        return jsonify(entries), 200
    elif request.method == "POST":
        title = None
        if request.args.get("title"):
            title = request.args.get("title")
        elif request.json and request.json["title"]:
            title = request.json["title"]
        else:
            return jsonify(error="Need a title to create entry"), 400

        doc = {"d_id": diaryId, "tags": [], "textBody": "This is the OG text.",
           "title": title}

        entry = Entry(doc)
        entry.save()

        # entry["_id"] = str(entry["_id"])
        return jsonify(entry)
        # entry = model.Entry(title)

        # for d in diaries:
        #     if d.id == diaryId:
        #         d.entries.append(entry)

        # return jsonify(entry.__dict__)

@app.route('/diaries/<diaryId>/entries/<entryId>', methods=['GET', 'DELETE', 'PUT'])
def modifyEntries(diaryId, entryId):
    # diary = [diary for diary in diaries if diary.id == diaryId]

    # if not len(diary):
    #     return jsonify(error=404, text="diary not found"), 404

    # diary = diary[0]

    # entries = diary.entries

    # entry = [entry for entry in entries if entry['id'] == entryId]
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
