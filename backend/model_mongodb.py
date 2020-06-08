import pymongo
import ssl
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

URI = 'mongodb+srv://client:mydiaryapp@cluster0-k792t.azure.mongodb.net/test?w=majority'


class Model(dict):
    """
    A simple model that wraps mongodb document
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    def save(self):
        if not self._id:
            self = self.make_db_ready(self)
            self['dateCreated'] = datetime.utcnow()
            self.collection.insert_one(self)
        else:  # if has _id, must already be added (bc insert() creates the _id)
            id = self["_id"]
            del self["_id"]
            self = self.make_db_ready(self)
            self.collection.update_one({"_id": ObjectId(id)}, {'$set': self})
            self["_id"] = id
        self = self.make_printable(self)

    def reload(self):
        if self._id:  # if in the db
            result = self.collection.find_one({"_id": ObjectId(self._id)})
            if result:
                self.update(result)  # updates created Diary (w/ id) to full doc
                self = self.make_printable(self)
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
    cluster = pymongo.MongoClient(URI, ssl=True,
                                  tlsAllowInvalidCertificates=False)
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
        if not entry:                            # if new entry
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

    # convert any string _ids to ObjectIds for storage in the db
    def make_db_ready(self, entry):
        if 'd_id' in entry:
            entry["d_id"] = ObjectId(entry["d_id"])
        return entry

    # convert any ObjectIds to strings
    def make_printable(self, entry):
        if '_id' in entry:
            entry["_id"] = str(entry["_id"])
        if 'd_id' in entry:
            entry["d_id"] = str(entry["d_id"])
        return entry

    # return the given list of Entry objects as a list printable objects
    @staticmethod
    def make_entries_printable(entries):
        for entry in entries:
            entry = Entry(entry).make_printable(entry)
        return entries

    # for internal use mostly (see above save)
    # This entry's _id doesn't need to be a valid entry. This function only
    #   checks if the specified _id is in the given diary JSON object.
    def find_entry_in_diary(self, diary):
        if diary and self._id:
            for id in diary["entries"]:  # entries = [ObjectIds]
                if self._id == str(id):
                    return self.collection.find_one({"_id": ObjectId(self._id)})
        return None

    # return the full, printable Diary object, if there is one for this Entry,
    #   else return None
    def get_diary(self):
        if self.d_id:           # if diary id (so diary should exist)
            diary = Diary({"_id": self.d_id})
            res = diary.reload()
            return (diary if res else None)
        return None

    # return True is this Entry has the Tag with the given title, False if not
    #   return None reload error
    def has_tag(self, title):
        if self.reload():
            return title in self['tags']
        return None

    # title is the unique tag title. If new tag, create tag first
    #   If a tag with the given title is already in this Entry, a duplicate
    #   will not be added.
    def add_tag(self, title):
        if self._id and self.reload() and not self.has_tag(title):
            tag = Tag().find_by_title(title, self.d_id)
            # if new tag, create in db
            if tag is None:
                Tag({"title": title, "d_id": self.d_id}).save()
            self["tags"].append(title)
            self.save()
            return True
        return False

    # Delete the Tag with the given title from this entry. returns True if
    #   successful, False if not.
    def delete_tag(self, title):
        if self._id and self.reload():
            tag = Tag().find_by_title(title, self.d_id)
            if tag is not None:
                self["tags"].remove(title)
                self.save()
                return True
        return False

    # return a list of Entries in entries that contain all tags in the given
    #   list of Tag titles
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


class Tag(Model):
    cluster = pymongo.MongoClient(URI)
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
                if self.title in entry['tags']:
                    entry['tags'].remove(self.title)
                    entry.save()
                    count = count + 1
            if super(Tag, self).remove():
                return count
        return None

    # convert any string _ids to ObjectIds for storage in the db
    def make_db_ready(self, tag):
        if 'd_id' in tag:
            tag["d_id"] = ObjectId(tag["d_id"])
        return tag

    # convert any ObjectIds to strings
    def make_printable(self, tag):
        if '_id' in tag:
            tag["_id"] = str(tag["_id"])
        if 'd_id' in tag:
            tag["d_id"] = str(tag["d_id"])
        return tag

    # return the full, printable Diary object, if there is one for this Tag,
    #   else return None
    def get_diary(self, diary):
        if self.d_id:           # if diary id (so diary should exist)
            diary = Diary({"_id": self.d_id})
            res = diary.reload()
            return (diary if res else None)
        return None

    # shouldn't be tags with same title in same diary --> can use title to get
    def find_by_title(self, title, d_id):
        tags = list(self.collection.find({"title": title,
                                          'd_id': ObjectId(d_id)}))
        if len(tags) > 0:
            tag = self.make_printable(Tag(tags[0]))
            return tag
        return None


class Diary(Model):
    cluster = pymongo.MongoClient(URI)
    dbStr = "myDiaryApp"
    db = cluster[dbStr]
    collection = db["diaries"]

    # if del diary, make sure to del all entries!
    def remove(self):
        if self.reload():
            for tag in self.get_tags():
                t = Tag(tag)
                t['_id'] = str(t['_id'])
                t.remove()
            for entry_id in self['entries']:
                # should already be strs but just in case
                entry = Entry({'_id': str(entry_id), 'd_id': str(self._id)})
                entry.remove()
        return super(Diary, self).remove()

    # convert any string _ids to ObjectIds for storage in the db
    def make_db_ready(self, diary):
        if "entries" in diary:
            entries = diary["entries"]
            for i in range(len(entries)):
                entries[i] = ObjectId(entries[i])
        return diary

    # convert any ObjectIds to strings
    def make_printable(self, diary):
        if '_id' in diary:
            diary["_id"] = str(diary["_id"])
        if 'entries' in diary:
            entries = diary["entries"]
            for i in range(len(entries)):
                entries[i] = str(entries[i])
        return diary

    # return a list of all diaries in the db as printable Diary objects
    def find_all(self):
        diaries = list(self.collection.find())
        for diary in diaries:  # change ObjectIDs->strs so is JSON serializable
            diary = self.make_printable(diary)
        return diaries

    # return a list of printable Diary objects that match the given title
    def find_by_title(self, title):
        diaries = list(self.collection.find({"title": title}))
        for diary in diaries:  # change all ObjectIDs to strs
            diary = self.make_printable(diary)
        return diaries

    # return a list of this Diary's entries as full, printable Entry objects
    def get_entries(self):
        items = []
        if self.reload():
            items = list(Entry.collection.find({"d_id": ObjectId(self._id)}))
            items = Entry.make_entries_printable(items)
        return items

    # return a list of this Diary's tags as full, printable Tag objects
    def get_tags(self):
        items = []
        if self._id:
            items = list(Tag.collection.find({"d_id": ObjectId(self._id)}))
        return items

    # return a list of this Diary's entries as full, printable Entry objects
    #   sorted by dateCreated. recent_first=True (default) if want to sort by
    #   most recent first. recent_first=False to sort by most recent last.
    def sort_entries_by_date_created(self, recent_first=True):
        sort = []
        if self.reload():
            for entry_id in self['entries']:
                entry = Entry({'_id': entry_id})
                entry.reload()
                entry = entry.make_printable(entry)
                sort.append(entry)
            sort = sorted(sort, key=lambda r: r["dateCreated"],
                          reverse=recent_first)
        return sort

    # return a list of this Diary's entries as full, printable Entry objects
    #   that conatain (in their title or text body) the text to search for
    def search_entries_for_text(self, string):
        res = []
        if self.reload():
            for entry_id in self['entries']:
                entry = Entry({'_id': entry_id})
                entry.reload()
                if string in entry['title'] or string in entry['textBody']:
                    entry = entry.make_printable(entry)
                    res.append(entry)
        return res
