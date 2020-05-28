import pytest
import pymongo
from bson import ObjectId
from model_mongodb import *


# TEST is a boolean const set in model_mongodb
def test_in_testing_mode():
    assert TEST is True


def test_diary_reload():
    diary_model = {"_id": None, "dateCreated": None, "entries": [], "title": ""}
    d_id = "5ececfbc28f47f5e4408ca45"
    diary = Diary({"_id": d_id})
    assert diary.reload() is True
    assert isinstance(diary["_id"], str) is True
    for item in diary_model:
        assert item in diary


def test_entry_gets_TEST():
    entry = Entry()
    clxns = entry.db.list_collection_names()
    expect = ["tests", "diaries", "entries"]
    for item in clxns:
        assert item in expect


def test_diary_gets_TEST():
    diary = Diary()
    clxns = diary.db.list_collection_names()
    expect = ["tests", "diaries", "entries"]
    for item in clxns:
        assert item in expect


def test_new_entry_no_diary():
    entry = Entry()
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
