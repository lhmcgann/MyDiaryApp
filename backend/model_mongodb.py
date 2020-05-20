import pymongo
from pymongo import MongoClient
from bson import ObjectId

uri = 'mongodb+srv://client:mydiaryapp@cluster0-k792t.azure.mongodb.net/test?re\
    tryWrites=true&w=majority'


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


# if need specific Entry, should init w/ d_id (diary id) and _id (entry id)
class Entry(Model):
    cluster = pymongo.MongoClient(uri)
    db = cluster["myDiaryApp"]
    collection = db["entries"]

    def reload(self):
        if self.d_id:  # if diary in the db
            self.remove("d_id", None)  # real entry doesn't need diary id field
            return super().reload()
        return False

    # for internal use mostly (see old reload); prereq: diary != none
    def find_entry_in_diary(self, diary):
        for id in diary["entries"]:  # entries = [ObjectIds]
            if self._id is str(id):
                return self.collection.find_one({"_id": ObjectId(self._id)})
        return None


class Diary(Model):
    cluster = pymongo.MongoClient(uri)
    db = cluster["myDiaryApp"]
    collection = db["diaries"]

    def find_all(self):
        diaries = list(self.collection.find())
        for diary in diaries:  # change ObjectIDs->strs so is JSON serializable
            diary = make_printable(diary)
        return diaries

    def find_by_title(self, title):
        diaries = list(self.collection.find({"title": title}))
        for diary in diaries:  # change ObjectIDs to strs
            diary = make_printable(diary)
        return diaries

    def make_printable(self, diary):
        diary["_id"] = str(diary["_id"])
        entries = diary["entries"]
        for i in range(len(entries)):
            entries[i] = str(entries[i])
        return diary

    # this successfully deletes all from db but html error bc wrong (nul) return
    # def delete_all(self):
    #     print("DELETED RESULT:" + str(self.collection.delete_many({}).raw_result))
