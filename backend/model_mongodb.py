import pymongo
import ssl
from pymongo import MongoClient
from bson import ObjectId

uri = 'mongodb+srv://client:mydiaryapp@cluster0-k792t.azure.mongodb.net/test?w=majority'


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
                self.update(result)  # updates created Diary (w/ id) to full doc
                self._id = str(self._id)  # may also need to convert entry ids
                return True
        return False

    def remove(self):
        if self._id:
            resp = self.collection.remove({"_id": ObjectId(self._id)})
            self.clear()
            return resp


class Entry(Model):
    cluster = pymongo.MongoClient(uri, ssl_cert_reqs=ssl.CERT_NONE)
    db = cluster["myDiaryApp"]
    collection = db["diaries"]

    def reload(self):
        if self.d_id and self._id:  # if in the db
            diary = Diary({"_id": self.d_id})
            res = diary.reload()  # reload full diary object
            if res:  # True or False
                res = find_entry_in_diary(diary)
            if res:  # None of entry dict
                self.remove("d_id", None)
                self.update(res)  # python dict update
                self._id = str(self._id)  # may also need to convert entry ids
                return True
        return False

    # for internal use mostly (see above reload); prereq: diary != none
    def find_entry_in_diary(self, diary):
        for entry in diary["entries"]:
            if self._id is str(entry._id):
                return entry
        return None


class Diary(Model):
    cluster = pymongo.MongoClient(uri)
    db = cluster["myDiaryApp"]
    collection = db["diaries"]

    def find_all(self):
        diaries = list(self.collection.find())
        for diary in diaries:  # change ObjectIDs->strs so is JSON serializable
            diary["_id"] = str(diary["_id"])
            for entry in diary["entries"]:
                entry["_id"] = str(entry["_id"])
        return diaries

    def find_by_title(self, title):
        diaries = list(self.collection.find({"title": title}))
        for diary in diaries:  # change ObjectIDs to strs
            diary["_id"] = str(diary["_id"])
        return diaries

    # this successfully deletes all from db but html error bc wrong (nul) return
    # def delete_all(self):
    #     print("DELETED RESULT:" + str(self.collection.delete_many({}).raw_result))
