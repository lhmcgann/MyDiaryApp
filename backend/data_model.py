import time
import json


class Diary:
    def __init__(self, title):
        self.title = title
        self.entries = []
        self.dateCreated = time.time()
        self.id = id(self)

    def sortEntriesMostRecent(self):
        return [entry.__dict__ for entry in sorted(this.entries, key=lambda entry: entry.dateCreated, reverse=True)]

    def sortEntriesLeastRecent(self):
        return [entry.__dict__ for entry in sorted(this.entries, key=lambda entry: entry.dateCreated)]

    def addEntry(self, entryTitle):
        newEntry = Entry(title)
        self.entries.append(newEntry)


class Entry:
    def __init__(self, title):
        self.title = title
        self.tags = []
        self.text = ""
        self.date = time.time()
        self.id = id(self)

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
