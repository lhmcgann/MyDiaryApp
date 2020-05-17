import pymongo
from pymongo import MongoClient
from bson import ObjectId

uri = 'mongodb+srv://client:mydiaryapp@cluster0-k792t.azure.mongodb.net/test?retryWrites=true&w=majority'


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
        else:  # if has _id, must already be added (bc insert() creates the _id)
            self.collection.update({"_id": ObjectId(self._id)}, self)
        self._id = str(self._id)

    def reload(self):
        if self._id:  # if in the db
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
    cluster = pymongo.MongoClient(uri)
    db = cluster["myDiaryApp"]
    collection = db["entries"]

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


class Diary(Model):
    cluster = pymongo.MongoClient(uri)
    db = cluster["myDiaryApp"]
    collection = db["diaries"]

    def find_all(self):
        diaries = list(self.collection.find())
        for diary in diaries:  # change ObjectIDs to strs
            diary["_id"] = str(diary["_id"])
        return diaries

    def find_by_title(self, title):
        diaries = list(self.collection.find({"title": title}))
        for diary in diaries:  # change ObjectIDs to strs
            diary["_id"] = str(diary["_id"])
        return diaries

    # this successfully deletes all from db but html error bc wrong (nul) return
    # def delete_all(self):
    #     print("DELETED RESULT:" + str(self.collection.delete_many({}).raw_result))
