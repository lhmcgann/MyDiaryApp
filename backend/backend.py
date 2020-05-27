from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
import ssl
from model_mongodb import Diary

app = Flask(__name__)
CORS(app)


@app.route('/diaries', methods=['GET', 'POST'])
def get_diaries():
    if request.method == "GET":
        diaries = Diary().find_all()
        # return {"diaries": diaries}, 200
        return jsonify([diary.__dict__ for diary in diaries]), 200
    elif request.method == 'POST':
        # diaryToAdd = request.get_json()
        # newDiary = Diary(diaryToAdd)
        # newDiary.save()
        title = request.args.get("title")
        if title is None:
            abort(400, "need to submit a title")

        newDiary = model.Diary(title)
        diaries.append(newDiary)
        resp = jsonify(newDiary.__dict__), 200
        return resp

    else:
        abort(400, "bad request")


@app.route('/diaries/<int:diaryId>', methods=['GET', 'PUT', 'DELETE'])
def retrieve_diary(diaryId):
    diary = [diary.__dict__ for diary in diaries if diary.id == diaryId]

    if not len(diary):
        abort(404, "diary not found")

    if request.method == "GET":
        return jsonify(diary[0])

    elif request.method == "PUT":
        title = request.args.get("title")

        if title:
            diary[0].title = title

        return jsonify(success=True)

    elif request.method == "DELETE":

        for i, d in enumerate(diaries):
            if d.id == diaryId:
                del diaries[i]

        return jsonify(success=True)

    else:
        abort(404, "not found")


# this needs to be done properly; still just copy pasted
@app.route('/diaries/<id>', methods=['GET', 'DELETE'])
def get_entries(id):
    diary = Diary({"_id": id})
    if request.method == "GET":
        diary.reload()
        return diary, 200
    if request.method == 'DELETE':
        success = diary.remove()
        return jsonify(success), 204  # set http response to show No Content

        # entryToAdd = request.get_json()
        # newEntry = Entry(entryToAdd)  # don't have an Entry class...
        # newEntry.save()
        # resp = jsonify(newEntry), 200
        # return resp
