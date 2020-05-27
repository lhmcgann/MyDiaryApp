import pytest
import pymongo
from bson import ObjectId
from model_mongodb import *


# to use for testing
def set_entry_test_db(entry):
    entry.db = entry.cluster["tests"]
    entry.collection = entry.db["entries"]


# to use for testing
def set_diary_test_db(diary):
    diary.db = diary.cluster["tests"]
    diary.collection = diary.db["diaries"]


def test_new_entry_no_diary():
    entry = Entry()
    set_entry_test_db(entry)
    assert entry.save() is False


def test_diary_reload_dne():
    diary = Diary()
    assert diary.reload() is False


# uri = 'mongodb+srv://client:mydiaryapp@cluster0-k792t.azure.mongodb.net/test?re\
#     tryWrites=true&w=majority'
# db = pymongo.MongoClient(uri)["myDiaryApp"]
# d_collection = db["diaries"]

# def test_find_all_diaries():
#     num_diaries = len(d_collection.find())
#     diaries = Diary().find_all()
#     assert num_diaries == len(diaries)
