import pytest
import pymongo
from bson import ObjectId
from model_mongodb import *


TEST_DB = "tests"


# class TEntry(Entry):
#     cluster = pymongo.MongoClient(uri, ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
#     db = cluster["tests"]
#     collection = db["entries"]
#
#
# class TDiary(Diary):
#     cluster = pymongo.MongoClient(uri, ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
#     db = cluster["tests"]
#     collection = db["diaries"]
#
#
# # to use for testing
# def set_entry_test_db(entry):
#     entry.db = entry.cluster["tests"]
#     entry.collection = entry.db["entries"]
#
#
# # to use for testing
# def set_diary_test_db(diary):
#     diary.db = diary.cluster["tests"]
#     diary.collection = diary.db["diaries"]


def test_setDB_entry():
    entry = Entry()

    clxns = entry.db.list_collection_names()
    expect = ["tags", "diaries", "entries"]
    for item in clxns:
        assert item in expect

    entry.setDB(TEST_DB)
    clxns = entry.db.list_collection_names()
    expect = ["tests", "diaries", "entries"]
    for item in clxns:
        assert item in expect


def test_setDB_diary():
    diary = Diary()

    clxns = diary.db.list_collection_names()
    expect = ["tags", "diaries", "entries"]
    for item in clxns:
        assert item in expect

    diary.setDB(TEST_DB)
    clxns = diary.db.list_collection_names()
    expect = ["tests", "diaries", "entries"]
    for item in clxns:
        assert item in expect


def test_new_entry_no_diary():
    entry = Entry()
    entry.setDB(TEST_DB)
    assert entry.save() is False


def test_diary_reload_dne():
    diary = Diary()
    diary.setDB(TEST_DB)
    assert diary.reload() is False


# uri = 'mongodb+srv://client:mydiaryapp@cluster0-k792t.azure.mongodb.net/test?re\
#     tryWrites=true&w=majority'
# db = pymongo.MongoClient(uri)["myDiaryApp"]
# d_collection = db["diaries"]

# def test_find_all_diaries():
#     num_diaries = len(d_collection.find())
#     diaries = Diary().find_all()
#     assert num_diaries == len(diaries)
