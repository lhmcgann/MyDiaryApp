import pymongo
import ssl
from pymongo import MongoClient
from bson import ObjectId
import time
import datetime

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
        return None


# if need specific Entry, should init w/ d_id (diary id) and _id (entry id)
class Entry(Model):
    cluster = pymongo.MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=False)
    dbStr = "myDiaryApp"
    db = cluster[dbStr]
    collection = db["entries"]

    # return: None if failed, True if inserted new, False if updated existing
    def save(self):
        diary = self.get_diary()                 # the filled Diary obj
        if not diary:
            return None
        super(Entry, self).save()
        entry = self.find_entry_in_diary(diary)  # the entry json obj
        if not entry:                       # if new entry
            diary["entries"].append(ObjectId(self._id))
            diary.save()
            return True
        return False

    def remove(self):
        diary = self.get_diary()             # the filled Diary obj
        if self.find_entry_in_diary(diary):  # remove id from diary's entries
            diary["entries"].remove(ObjectId(self._id))
            diary.save()
            return super(Entry, self).remove()  # remove from entries collection
        else:
            return None

    def get_entries_with_diary_id(self, diaryId):
        items = list(self.collection.find({"d_id": diaryId}))
        return items

    def get_diary(self):
        if self.d_id:           # if diary id (so diary should exist)
            diary = Diary({"_id": self.d_id})
            res = diary.reload()
            return (diary if res else None)
        return None

    @staticmethod
    def filter_with_tags(entries, tags):
        def entry_has_tag(entry):
            entry_tags = set(entry["tags"])
            for tag in tags:
                if tag not in entry_tags:
                    return False
            return True

        filtered_entries = list(filter(entry_has_tag, entries))
        return filtered_entries

    @staticmethod
    def sort_entries(entries, mostRecent = True):
        return sorted(entries, key = lambda entry: time.mktime(entry["dateCreated"].timetuple()), reverse=mostRecent)

    @staticmethod
    def make_printable(entries):
        for entry in entries:
            entry["_id"] = str(entry["_id"])
        return entries

    def find_by_id(self, entryId):
        entry = list(self.collection.find({"_id": ObjectId(entryId)}))

        return Entry.make_printable(entry)



    # for internal use mostly (see above save)
    # This entry's _id doesn't need to be a valid entry. This function only
    #   checks if the specified _id is in the given diary JSON object.
    def find_entry_in_diary(self, diary):
        if diary and self._id:
            for id in diary["entries"]:  # entries = [ObjectIds]
                if self._id == str(id):
                    return self.collection.find_one({"_id": ObjectId(self._id)})
        return None


class Diary(Model):
    cluster = pymongo.MongoClient(uri)
    dbStr = "myDiaryApp"
    db = cluster[dbStr]
    collection = db["diaries"]

    # if del diary, make sure to del all entries!
    def remove(self):
        if self.reload():
            for entry_id in self['entries']:
                # should already be strs but just in case
                entry = Entry({'_id': str(entry_id), 'd_id': str(self._id)})
                entry.remove()
        return super(Diary, self).remove()

    def find_all(self):
        diaries = list(self.collection.find())
        for diary in diaries:  # change ObjectIDs->strs so is JSON serializable
            diary = self.make_printable(diary)
        return diaries

    def get_all_diaries(self):
        diaries = self.find_all()

        for diary in diaries:
            diaryId = str(diary["_id"])
            diary["entries"] = Entry.make_printable(Entry().get_entries_with_diary_id(diaryId))

        return diaries

    def find_by_title(self, title):
        diaries = list(self.collection.find({"title": title}))
        for diary in diaries:  # change ObjectIDs to strs
            diary = self.make_printable(diary)
        return diaries

    def find_by_id(self, diaryId):
        diaries = list(self.collection.find({"_id": ObjectId(diaryId)}))
        if len(diaries):
            diaryId = str(diaries[0]["_id"])
            diaries[0]["entries"] = Entry.make_printable(Entry().get_entries_with_diary_id(diaryId))

        return diaries

    def make_printable(self, diary):
        diary["_id"] = str(diary["_id"])
        diary["entries"] = Entry.make_printable(Entry().get_entries_with_diary_id(diary["_id"]))
        return diary

    # this successfully deletes all from db but html error bc wrong (nul) return
    # def delete_all(self):
    #     print("DELETED RESULT:" + str(self.collection.delete_many({}).raw_result))
