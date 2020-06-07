import pymongo
import ssl
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from operator import itemgetter

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
            self['dateCreated'] = datetime.utcnow()
            self.collection.insert_one(self)
        else:  # if has _id, must already be added (bc insert() creates the _id)
            # TODO: any better way to handle _id's?
            id = self["_id"]
            self = self.make_db_ready(self)
            self.collection.update_one({"_id": ObjectId(id)}, {'$set': self})
            self["_id"] = id
        self = self.make_printable(self)

    def reload(self):
        if self._id:  # if in the db
            result = self.collection.find_one({"_id": ObjectId(self._id)})
            if result:
                self.update(result)  # updates created doc (w/ id) to full doc
                # TODO: call a make_printable() function?
                # self._id = str(self._id)  # may also need to convert entry ids
                self.make_printable(self)
                return True
        return False

    def remove(self):
        if self._id:
            resp = self.collection.delete_one({"_id": ObjectId(self._id)})
            self.clear()
            return resp
        return None

    def make_db_ready(self, toDB):
        del toDB["_id"]
        return toDB

    def make_printable(self, toPrintable):
        return toPrintable


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
            diary["entries"].remove(self._id)
            diary.save()
            return super(Entry, self).remove()  # remove from entries collection
        else:
            return None

    def make_db_ready(self, entry):
        entry = super(Entry, self).make_db_ready(entry)
        if entry["tags"]:
            tags = entry["tags"]
            for i in range(len(tags)):
                tags[i] = ObjectId(tags[i])
        return entry

    def make_printable(self, entry):
        if '_id' in entry:
            entry["_id"] = str(entry["_id"])
        if 'd_id' in entry:
            entry["d_id"] = str(entry["d_id"])
        if 'tags' in entry:
            tags = entry["tags"]
            for i in range(len(tags)):
                tags[i] = str(tags[i])
        return entry

    def get_diary(self):
        if self.d_id:           # if diary id (so diary should exist)
            diary = Diary({"_id": self.d_id})
            res = diary.reload()
            return (diary if res else None)
        return None

    # for internal use mostly (see above save)
    # This entry's _id doesn't need to be a valid entry. This function only
    #   checks if the specified _id is in the given diary JSON object.
    def find_entry_in_diary(self, diary):
        if diary and self._id:
            for id in diary["entries"]:  # entries = [ObjectIds]
                if self._id == str(id):
                    return self.collection.find_one({"_id": ObjectId(self._id)})
        return None

    # title is the unique tag title. If new tag, create tag
    def add_tag(self, title):
        if self._id and self.reload():
            tag = Tag().find_by_title(title, self.d_id)
            # if new tag, create in db
            if tag is None:
                Tag({"title": title, "d_id": self.d_id}).save()
                tag = Tag().find_by_title(title, self.d_id)
            self["tags"].append(tag["_id"])
            self.save()
            return True
        return False

    def delete_tag(self, title):
        if self._id and self.reload():
            tag = Tag().find_by_title(title, self.d_id)
            if tag is not None:
                tag.reload()
                id = tag["_id"]
                self["tags"].remove(id)
                self.save()
                return True
                # return tag.remove() --> don't wan't to actually del from DB!
        return False


class Tag(Model):
    cluster = pymongo.MongoClient(uri)
    dbStr = "myDiaryApp"
    db = cluster[dbStr]
    collection = db["tags"]

    def save(self):
        if self._id:
            super(Tag, self).save()
        elif self.title and self.d_id:
            diary = self.get_diary(self.d_id)
            if diary:
                tag = self.find_by_title(self.title, self.d_id)
                if tag:
                    self['_id'] = tag['_id']
                super(Tag, self).save()

    def get_diary(self, diary):
        if self.d_id:           # if diary id (so diary should exist)
            diary = Diary({"_id": self.d_id})
            res = diary.reload()
            return (diary if res else None)
        return None

    def reload(self):
        if self._id:
            return super(Tag, self).reload()
        elif self.title and self.d_id:
            tag = self.find_by_title(self.title, self.d_id)
            if tag:
                self.update(tag)
                return True
        return False

    def remove(self):
        if self.title and self.d_id:
            self = self.find_by_title(self.title, self.d_id)
            if not self:
                return -1
            diary = Diary({'_id': self.d_id})
            diary.reload()
            count = 0
            for entry_id in diary['entries']:
                entry = Entry({'_id': entry_id})
                entry.reload()
                if self._id in entry['tags']:
                    entry['tags'].remove(self._id)
                    entry.save()
                    count = count + 1
            if super(Tag, self).remove():
                return count
        return None

    # shouldn't be tags with same title in same diary --> can use title to get
    def find_by_title(self, title, d_id):
        tags = list(self.collection.find({"title": title, 'd_id': d_id}))
        if len(tags) > 0:
            tag = self.make_printable(Tag(tags[0]))
            return tag
        return None

    def make_printable(self, tag):
        if '_id' in tag:
            tag["_id"] = str(tag["_id"])
        if 'd_id' in tag:
            tag["d_id"] = str(tag["d_id"])
        return tag


class Diary(Model):
    cluster = pymongo.MongoClient(uri)
    dbStr = "myDiaryApp"
    db = cluster[dbStr]
    collection = db["diaries"]

    def find_all(self):
        diaries = list(self.collection.find())
        for diary in diaries:  # change ObjectIDs->strs so is JSON serializable
            diary = self.make_printable(diary)
        return diaries

    def find_by_title(self, title):
        diaries = list(self.collection.find({"title": title}))
        for diary in diaries:  # change ObjectIDs to strs
            diary = self.make_printable(diary)
        return diaries

    # tags is a string array of tag names
    def find_by_at_least_one_tag(self, tags):
        return None

    def make_db_ready(self, diary):
        diary = super(Diary, self).make_db_ready(diary)
        if diary["entries"]:
            entries = diary["entries"]
            for i in range(len(entries)):
                entries[i] = ObjectId(entries[i])
        return diary

    def make_printable(self, diary):
        if '_id' in diary:
            diary["_id"] = str(diary["_id"])
        if 'entries' in diary:
            entries = diary["entries"]
            for i in range(len(entries)):
                entries[i] = str(entries[i])
        return diary

    def sort_entries_by_date_created(self, recent_last=True):
        sort = []
        if self.reload():
            for entry_id in self['entries']:
                entry = Entry({'_id': entry_id})
                entry.reload()
                sort.append(entry)
            sort = sorted(sort, key=lambda r: r["dateCreated"],
                          reverse=recent_last)
        return sort

    # this successfully deletes all from db but html error bc wrong (nul) return
    # def delete_all(self):
    #     print("DELETED RESULT:" + str(self.collection.delete_many({}).raw_result))
