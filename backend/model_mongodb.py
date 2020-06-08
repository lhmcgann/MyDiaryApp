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
        """
        Saves this object to the db.

        If new object (i.e. no _id), inserts new and generates a dateCreated,
        else updates the existing db object.
        """
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
        """
        Fills this Model with the rest of its information from the db.

        Makes this Model printable. Returns True on success, False on failure.
        """
        if self._id:  # if in the db
            result = self.collection.find_one({"_id": ObjectId(self._id)})
            if result:
                self.update(result)  # updates created Diary (w/ id) to full doc
                self = self.make_printable(self)
                return True
        return False

    def remove(self):
        """
        Removes this Model object from the database and clears this object.

        Returns the db response on success, None if failed (no _id in this
        object)
        """
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

    def save(self):
        """
        Save this Entry to the db.

        Insert if new, else update existing.
        return: None if failed, True if inserted new, False if updated existing
        """
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
        """
        Remove this Entry from the db and remove its id from the Diary it was in
        """
        diary = self.get_diary()             # the filled Diary obj
        if self.find_entry_in_diary(diary):  # remove id from diary's entries
            diary["entries"].remove(self._id)
            diary.save()
            return super(Entry, self).remove()  # remove from entries collection
        else:
            return None

    def make_db_ready(self, entry):
        """ Convert any string _ids to ObjectIds for storage in the db """
        if 'd_id' in entry:
            entry["d_id"] = ObjectId(entry["d_id"])
        return entry

    def make_printable(self, entry):
        """ Convert any ObjectIds to strings """
        if '_id' in entry:
            entry["_id"] = str(entry["_id"])
        if 'd_id' in entry:
            entry["d_id"] = str(entry["d_id"])
        return entry

    @staticmethod
    def make_entries_printable(entries):
        """ Get the given list of Entry objects as a list printable objects """
        for entry in entries:
            entry = Entry(entry).make_printable(entry)
        return entries

    def find_entry_in_diary(self, diary):
        """
        Check if this Entry's _id is in the given Diary object.

        For internal use mostly. Returns the result of the db query, None if
        fails.
        """
        if diary and self._id:
            for id in diary["entries"]:  # entries = [ObjectIds]
                if self._id == str(id):
                    return self.collection.find_one({"_id": ObjectId(self._id)})
        return None

    def get_diary(self):
        """
        Get the Diary object of the Diary this Entry is in.

        Returns the full, printable Diary object if there is one, else None.
        """
        if self.d_id:           # if diary id (so diary should exist)
            diary = Diary({"_id": self.d_id})
            res = diary.reload()
            return (diary if res else None)
        return None

    def has_tag(self, title):
        """
        Checks the Tag with the given title is in this Entry.

        Return True if yes, False if not, None if Entry reload error.
        """
        if self.reload():
            return title in self['tags']
        return None

    def add_tag(self, title):
        """
        Add a Tag with the given title to this Entry.

        If a Tag with the given title is already in this Entry, a duplicate
        will not be added. If the Tag does not exist in the Diary, a new Tag
        will be added to the db. Returns True if successful, False if not.
        """
        if self._id and self.reload() and not self.has_tag(title):
            tag = Tag().find_by_title(title, self.d_id)
            # if new tag, create in db
            if tag is None:
                Tag({"title": title, "d_id": self.d_id}).save()
            self["tags"].append(title)
            self.save()
            return True
        return False

    def delete_tag(self, title):
        """
        Delete the Tag with the given title from this Entry.

        Returns True if successful, False if not.
        """
        if self._id and self.reload():
            tag = Tag().find_by_title(title, self.d_id)
            if tag is not None:
                self["tags"].remove(title)
                self.save()
                return True
        return False

    @staticmethod
    def filter_with_tags(entries, tags):
        """
        Return a list of Entries in entries that match all tags in tags.

        Entries shold be a list of full Entry objects.
        Tags is a list of tag names to filter by.
        """
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
        """
        Save this Tag to the db.

        Tag titles are unique within Diaries, so if the title is already in the
        Diary with the d_id of this Tag, the tag will be updated rather than
        creating another tag with the same title.
        """
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
        """
        Fills this Tag with the rest of its information from the db.

        Makes this Tag printable. Returns True on success, False on failure.
        """
        if self._id:
            return super(Tag, self).reload()
        elif self.title and self.d_id:
            tag = self.find_by_title(self.title, self.d_id)
            if tag:
                self.update(tag)
                return True
        return False

    def remove(self):
        """
        Remove this Tag from the database and from all Entries it is in.

        Returns the number of Entries this Tag was removed from, or None on
        failure (this Tag object must contain an _id or a title and diary id).
        """
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

    def make_db_ready(self, tag):
        """ Convert any string _ids to ObjectIds for storage in the db """
        if 'd_id' in tag:
            tag["d_id"] = ObjectId(tag["d_id"])
        return tag

    def make_printable(self, tag):
        """ Convert any ObjectIds to strings """
        if '_id' in tag:
            tag["_id"] = str(tag["_id"])
        if 'd_id' in tag:
            tag["d_id"] = str(tag["d_id"])
        return tag

    def get_diary(self, diary):
        """
        Get the Diary object of the Diary this Tag is in.

        Returns the full, printable Diary object if there is one, else None.
        """
        if self.d_id:           # if diary id (so diary should exist)
            diary = Diary({"_id": self.d_id})
            res = diary.reload()
            return (diary if res else None)
        return None

    def find_by_title(self, title, d_id):
        """
        Find a Tag with the given title in the Diary with the given _id.

        Return the printable Tag on success, else None.
        """
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

    def remove(self):
        """
        Remove this Diary and all of its Entries and Tags from the db.
        """
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

    def make_db_ready(self, diary):
        """ Convert any string _ids to ObjectIds for storage in the db """
        if "entries" in diary:
            entries = diary["entries"]
            for i in range(len(entries)):
                entries[i] = ObjectId(entries[i])
        return diary

    def make_printable(self, diary):
        """ Convert any ObjectIds to strings """
        if '_id' in diary:
            diary["_id"] = str(diary["_id"])
        if 'entries' in diary:
            entries = diary["entries"]
            for i in range(len(entries)):
                entries[i] = str(entries[i])
        return diary

    def find_all(self):
        """
        Return a list of all Diaries in the db as printable Diary objects.
        """
        diaries = list(self.collection.find())
        for diary in diaries:  # change ObjectIDs->strs so is JSON serializable
            diary = self.make_printable(diary)
        return diaries

    def find_by_title(self, title):
        """
        Return a list of printable Diary objects that match the given title.
        """
        diaries = list(self.collection.find({"title": title}))
        for diary in diaries:  # change all ObjectIDs to strs
            diary = self.make_printable(diary)
        return diaries

    def get_entries(self):
        """
        Return a list of this Diary's Entries as full, printable Entry objects.
        """
        items = []
        if self.reload():
            items = list(Entry.collection.find({"d_id": ObjectId(self._id)}))
            items = Entry.make_entries_printable(items)
        return items

    def get_tags(self):
        """
        Return a list of this Diary's tags as full, printable Tag objects.
        """
        items = []
        if self._id:
            items = list(Tag.collection.find({"d_id": ObjectId(self._id)}))
        return items

    def sort_entries_by_date_created(self, recent_first=True):
        """
        Sort this Diary's entries by date created.

        recent_first=True (default) to sort by most recent first.
        recent_first=False to sort by most recent last.
        Return a list of the sorted Entries as full, printable Entry objects.
        """
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

    def search_entries_for_text(self, string):
        """
        Search this Diary's Entries for a text string.

        Return a list of Entries (as full, printable Entry objects) that contain
        (in their title or text body) the text string to search for.
        """
        res = []
        if self.reload():
            for entry_id in self['entries']:
                entry = Entry({'_id': entry_id})
                entry.reload()
                if string in entry['title'] or string in entry['textBody']:
                    entry = entry.make_printable(entry)
                    res.append(entry)
        return res
