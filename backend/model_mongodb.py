import pymongo
import ssl
from pymongo import MongoClient
from bson import ObjectId

uri = 'mongodb+srv://client:mydiaryapp@cluster0-k792t.azure.mongodb.net/test?w=majority'
TEST = True


class Model(dict):
    """
    A simple model that wraps mongodb document
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    def save(self):
        if not self._id:
            self.collection.insert_one(self)
        else:  # if has _id, must already be added (bc insert() creates the _id)
            # TODO: any better way to handle _id's?
            id = self["_id"]
            del self["_id"]
            self.collection.update_one({"_id": ObjectId(id)}, {'$set': self})
            self["_id"] = id
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
            resp = self.collection.delete_one({"_id": ObjectId(self._id)})
            self.clear()
            return resp


# if need specific Entry, should init w/ d_id (diary id) and _id (entry id)
class Entry(Model):
    cluster = pymongo.MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=False)
    dbStr = ("tests" if TEST else "myDiaryApp")
    db = cluster[dbStr]
    collection = db["entries"]

    def save(self):
        diary = self.get_diary()                 # the filled Diary obj
        if not diary:
            return False
        del self["d_id"]
        super(Entry, self).save()
        entry = self.find_entry_in_diary(diary)  # the entry json obj
        if not entry:                       # if new entry
            diary["entries"].append(ObjectId(self._id))
            diary.save()
            return True
        return False

    def reload(self):
        if self.d_id:                  # if diary in the db
            self.remove("d_id", None)  # real entry doesn't need diary id field
            return super(Entry, self).reload()
        return False

    def remove(self):
        diary = get_diary()     # the filled Diary obj
        if diary:               # remove id from diary's entries array
            diary.collection.update_one({'_id': diary._id},
                                        {'$pull': {'entries': ObjectId(self._id)}})
        return super(Entry, self).remove()   # remove from entries collection

    def get_diary(self):
        if self.d_id:           # if diary id (so diary should exist)
            diary = Diary({"_id": self.d_id})
            res = diary.reload()
            return (diary if res else None)
        return None

    # for internal use mostly (see above save)
    def find_entry_in_diary(self, diary):
        if diary: #and self._id:
            for id in diary["entries"]:  # entries = [ObjectIds]
                if self._id is str(id):
                    return self.collection.find_one({"_id": ObjectId(self._id)})
        return None


class Diary(Model):
    cluster = pymongo.MongoClient(uri)
    dbStr = ("tests" if TEST else "myDiaryApp")
    db = cluster[dbStr]
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
