import pymongo
from pymongo import MongoClient
from bson import ObjectId


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
                {"_id": ObjectId(self._id)}, self)
        self._id = str(self._id)

    def reload(self):
        if self._id:
            result = self.collection.find_one({"_id": ObjectId(self._id)})
            if result:
                self.update(result)
                self._id = str(self._id)
                return True
        return False

    def remove(self):
        if self._id:
            resp = self.collection.remove({"_id": ObjectId(self._id)})
            self.clear()
            return resp


class Entry(Model):
    uri = 'mongodb+srv://client:mydiaryapp@cluster0-k792t.azure.mongodb.net/test?retryWrites=true&w=majority'
    cluster = pymongo.MongoClient(uri)
    db = cluster["diary1"]
    collection = db["diary1"]

    def find_all(self):
        entries = list(self.collection.find())
        for entry in entries:
            entry["_id"] = str(entry["_id"])
        return entries

    def find_by_title(self, title):
        entries = list(self.collection.find({"title": title}))
        for entry in entries:
            entry["_id"] = str(entry["_id"])
        return entries

    def delete_all(self):
        collection.delete_many({})
