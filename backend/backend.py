from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import pymongo
import ssl



app = Flask(__name__)
CORS(app)



class Model(dict):
    """
    A simple model that wraps mongodb document
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    def save(self):
        if not self._id:
            self.collection.insert(self)
        else:
            self.collection.update(
                { "_id": ObjectId(self._id) }, self)
        self._id = str(self._id)

    def reload(self):
        if self._id:
            result = self.collection.find_one({"_id": ObjectId(self._id)})
            if result :
                self.update(result)
                self._id = str(self._id)
                return True
        return False

    def remove(self):
        if self._id:
            resp = self.collection.remove({"_id": ObjectId(self._id)})
            self.clear()
            return resp


class User(Model):
    cluster = pymongo.MongoClient('localhost', 27017)
    db = cluster["diary"]
    collection = db["diary"]
    def find_all(self):
        users = list(self.collection.find())
        for user in users:
              user["_id"] = str(user["_id"])
        return users

    def find_by_name(self, name):
        users = list(self.collection.find({"name": name}))
        for user in users:
              user["_id"] = str(user["_id"])
        return users


@app.route('/users', methods=['GET', 'POST'])
def get_users():
    if request.method == "GET":
        diaries = User().find_all()
        return {"diaries": diaries}, 200
    if request.method == 'POST':
        userToAdd = request.get_json()
        newUser = User(userToAdd)
        newUser.save()
        resp = jsonify(newUser), 200
        return resp