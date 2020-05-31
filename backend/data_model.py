import time
import json
import datetime

class Diary:
    def __init__(self, title=""):
        self.title = title
        self.entries = []
        self.dateCreated = datetime.datetime.now()
        self.id = id(self)

    def sortEntriesMostRecent(self):
        return [entry.__dict__ for entry in sorted(this.entries, key=lambda entry: entry.dateCreated, reverse=True)]

    def sortEntriesLeastRecent(self):
        return [entry.__dict__ for entry in sorted(this.entries, key=lambda entry: entry.dateCreated)]

    def addEntry(self, entryTitle):
        newEntry = Entry(title)
        self.entries.append(newEntry)

    def appendEntry(self, entry):
        self.entries.append(entry)

    def json(self):
        jsonObject = self.__dict__
        jsonObject["entries"] = [entry.__dict__ if isinstance(entry, Entry) else entry for entry in jsonObject["entries"]]
        return jsonObject

    def removeEntry(self, entryId):
        for i, entry in enumerate(self.entries):
            if entry.id == entryId:
                del self.entries[i]
                break



class Entry:
    def __init__(self, title=""):
        self.title = title
        self.tags = []
        self.text = ""
        self.date = datetime.datetime.now()
        self.id = id(self)

    def updateEntry(self, title, tags, text):
        self.title = title
        self.text = text

        for tag in tags:
            self.add_tag(tag)

    def update_title(self, title):
        self.title = title

    def update_text(self, text):
        self.text = text

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)

    def json(self):
        return self.__dict__
