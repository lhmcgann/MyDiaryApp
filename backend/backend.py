from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from flask import abort
from model_mongodb import *

app = Flask(__name__)
CORS(app)


@app.route('/diaries', methods=['GET', 'POST'])
def retrieve_diaries():
    if request.method == 'GET':
        diaries = Diary().find_all()
        return {"diaries": diaries}, 200
    elif request.method == 'POST':
        if request.args.get("title") is not None:
            title = request.args.get("title")
        elif request.json and "title" in request.json is not None:
            title = request.json["title"]
        else:
            return jsonify(error="need to enter a title"), 400

        newDiary = Diary({"title": title, "entries": []})
        newDiary.save()
        resp = jsonify(newDiary.make_printable(newDiary)), 200
        return resp
    else:
        return jsonify(error="bad request"), 400


@app.route('/diaries/<diaryId>', methods=['GET', 'PUT', 'DELETE'])
def retrieve_diary(diaryId):
    diary = Diary({'_id': diaryId})

    if not diary.reload():
        return jsonify(error=404, text="diary not found"), 404

    if request.method == "GET":
        # frontend expects embedded entries
        diary["entries"] = diary.get_entries()
        return jsonify(diary)

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
    diary = Diary({'_id': diaryId})

    if not diary.reload():
        return jsonify(error=404, text="diary not found"), 404

    if request.method == "GET":
        entries = diary.get_entries()
        tags = request.args.get("tags")
        sortBy = request.args.get("sortBy")

        if tags:
            entries = Entry.filter_with_tags(entries, tags)
        if sortBy:
            sortBy = sortBy.lower()
            sortBy_to_ascending = {"mostrecent": True, "leastrecent": False}

            if sortBy in sortBy_to_ascending:
                res = sortBy_to_ascending[sortBy]
                entries = diary.sort_entries_by_date_created(res)

        return jsonify(Entry.make_entries_printable(entries)), 200

    elif request.method == "POST":
        title = None
        if request.args.get("title"):
            title = request.args.get("title")
        elif request.json and "title" in request.json:
            title = request.json["title"]
        else:
            return jsonify(error="Need a title to create entry"), 400

        doc = {"d_id": diaryId, "tags": [], "textBody": "", "title": title}

        entry = Entry(doc)
        entry.save()

        return jsonify(entry)


@app.route('/diaries/<diaryId>/entries/<entryId>/tags/<tag>',
           methods=['DELETE', 'POST'])
def modifyTags(diaryId, entryId, tag):
    entry = Entry({'_id': entryId, 'd_id': diaryId})

    if not entry.reload():
        return jsonify(error=404, text="entry not found"), 404

    if request.method == "DELETE":
        if not entry.has_tag(tag):
            return jsonify(error="Tag not found"), 404
        else:
            entry.delete_tag(tag)
            return jsonify(sucess=True)
    elif request.method == "POST":
        if entry.has_tag(tag):
            return jsonify(error="No duplicate tags"), 400
        else:
            entry.add_tag(tag)
            return jsonify(sucess=True)


@app.route('/diaries/<diaryId>/entries/<entryId>', methods=['GET', 'PUT',
           'DELETE'])
def modifyEntries(diaryId, entryId):
    entry = Entry({'_id': entryId, 'd_id': diaryId})

    if not entry.reload():
        return jsonify(error=404, text="entry not found"), 404

    if request.method == "GET":
        return jsonify(entry)
    elif request.method == "PUT":
        title = entry["title"]
        text = entry["textBody"]

        if request.args.get("title"):
            title = request.args.get("title")
        elif request.json and "title" in request.json:
            title = request.json["title"]

        if request.args.get("text"):
            text = request.args.get("text")
        elif request.json and "text" in request.json:
            text = request.json["text"]

        if request.args.get("tags"):
            return jsonify(error="Tags must be in the request body not in the \
                params"), 400
        elif request.json and "tags" in request.json:
            for tag in list(set(request.json["tags"])):
                entry.add_tag(tag)

        entry["title"] = title
        entry["textBody"] = text
        entry.save()

        return jsonify(success=True)

    elif request.method == "DELETE":
        succeed = True if entry.remove() else False

        return jsonify(success=succeed)
