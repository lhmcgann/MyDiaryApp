import pytest
import pymongo
from bson import ObjectId
from model_mongodb import *


# TODO: figure out how to reset after tests to make it more reliable/indp


# TEST is a boolean const set in model_mongodb
def test_in_testing_mode():
    assert TEST is True


def test_diary_save_new():
    doc = {"title": "test_diary_save_new", "dateCreated": "TODO: need Date()",
           "entries": []}
    diary = Diary(doc)

    # before save, make sure not in db
    assert diary.collection.find_one({"title": "test_diary_save_new"}) is None

    diary.save()
    res = diary.collection.find_one({"title": "test_diary_save_new"})
    assert res is not None
    for item in res:
        assert item in diary


def test_diary_save_old():
    title = "test_diary_save_new"
    doc = Diary.collection.find_one({"title": title})
    assert doc is not None

    diary = Diary(doc)
    for item in doc:
        assert item in diary

    # make change
    newDate = "something new"
    diary["dateCreated"] = newDate
    diary.save()
    assert isinstance(diary._id, str)
    res = Diary.collection.find_one({"title": title})
    assert res["dateCreated"] == newDate


# removes the diary inserted in test_diary_save_new to test and help reset
def test_diary_remove():
    title = "test_diary_save_new"
    res = Diary.collection.find_one({"title": title})
    assert res is not None

    id = res["_id"]
    assert isinstance(id, ObjectId)
    id = str(id)
    assert isinstance(id, str)

    diary = Diary({"_id": id})
    diary.remove()
    assert (diary == {}) is True


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


def test_new_entry_with_diary():
    d_id = "5ececfbc28f47f5e4408ca45"
    doc = {"d_id": d_id, "tags": [], "textBody": "blah",
           "title": "test_new_entry_with_diary"}
    entry = Entry(doc)

    assert entry.save() is True

    res = entry.collection.find_one({"title": "test_new_entry_with_diary"})
    assert res is not None
    assert "d_id" not in res

    # check all other items made it into db
    del doc["d_id"]
    for item in doc:
        assert item in res

    # check entry _id got into diary's entries array
    diary = Diary({"_id": d_id})
    diary.reload()
    assert res["_id"] in diary["entries"]


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
