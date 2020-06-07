import pytest
import pymongo
from bson import ObjectId
from model_mongodb import *


# the ObjectId of the diary in the tests collection
D_ID = "5ececfbc28f47f5e4408ca45"


def test_setup():
    # enter "test mode": use testing db
    Entry.dbStr = Diary.dbStr = "tests"
    Entry.db = Entry.cluster[Entry.dbStr]
    Entry.collection = Entry.db["entries"]
    Diary.db = Diary.cluster[Diary.dbStr]
    Diary.collection = Diary.db["diaries"]

    assert Entry.collection.find_one({}) is None
    assert Diary.collection.find_one({"_id": ObjectId(D_ID)}) is not None


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


def test_diary_reload_no_id():
    diary = Diary()
    assert diary.reload() is False

    d2 = Diary({"random field": "random value"})
    assert diary.reload() is False


def test_diary_reload_bad_id():
    d2 = Diary({"_id": ObjectId()})
    assert d2.reload() is False


def test_diary_reload():
    diary_model = {"_id": None, "dateCreated": None, "entries": [], "title": ""}
    diary = Diary({"_id": D_ID})
    assert diary.reload() is True
    assert isinstance(diary["_id"], str) is True
    for item in diary_model:
        assert item in diary


def test_diary_remove_no_id():
    diary = Diary()
    assert diary.remove() is None


def test_diary_remove_bad_id():
    diary = Diary({"_id": ObjectId()})
    assert diary.remove().deleted_count == 0


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
    assert (diary == {}) is False
    diary.remove()
    assert (diary == {}) is True


def test_entry_get_diary_no_id():
    entry = Entry()
    assert entry.get_diary() is None


def test_entry_get_diary_bad_id():
    id = ObjectId()
    entry = Entry({"d_id": id})
    assert entry.get_diary() is None


def test_entry_get_diary():
    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    entry = Entry({"d_id": D_ID})
    res = entry.get_diary()
    for item in diary:
        if item == "_id":
            assert str(diary[item]) == res[item]
        else:
            assert diary[item] == res[item]


def test_find_entry_in_none_diary():
    entry = Entry()
    res = entry.find_entry_in_diary(None)
    assert res is None


def test_find_entry_in_diary_no_entry_id():
    entry = Entry()
    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    assert diary is not None
    res = entry.find_entry_in_diary(diary)
    assert res is None


def test_find_entry_in_diary_not_found():
    entry = Entry({"_id": ObjectId()})
    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    assert diary is not None
    res = entry.find_entry_in_diary(diary)
    assert res is None


def test_find_entry_in_diary_found():
    title = "test_find_entry_in_diary_found"
    doc = {"title": title, "tags": [], "textBody": "nothing",
           "dateCreated": "TODO"}
    # put entry in db (to give it an _id) and then find in db
    Entry.collection.insert_one(doc)
    from_db = Entry.collection.find_one({"title": title})
    assert from_db is not None

    # put entry's _id into diary entries array
    id = from_db["_id"]
    Diary.collection.update_one({"_id": ObjectId(D_ID)},
                                {'$push': {'entries': id}})

    entry = Entry({"_id": str(id)})
    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    assert diary is not None
    res = entry.find_entry_in_diary(diary)
    assert res == from_db


def test_entry_save_no_diary():
    entry = Entry()
    assert entry.save() is None  # None means error, nothing happened


def test_entry_save_new_with_diary():
    title = "test_new_entry_with_diary"
    doc = {"d_id": D_ID, "tags": [], "textBody": "This is the OG text.",
           "title": title}
    entry = Entry(doc)

    assert entry.save() is True

    res = entry.collection.find_one({"title": title})
    assert res is not None
    for item in doc:
        assert item in res
        assert doc[item] == res[item]

    # check entry _id got into diary's entries array
    diary = Diary({"_id": D_ID})
    diary.reload()
    assert res["_id"] in diary["entries"]


def test_entry_save_old_with_diary():
    title = "test_new_entry_with_diary"
    from_db = Entry.collection.find_one({"title": title})
    assert from_db is not None
    id = str(from_db["_id"])

    entry = Entry({"_id": id, "d_id": D_ID})
    entry.reload()
    assert entry["textBody"] == "This is the OG text."
    entry["textBody"] = "this is the NEW text"
    assert entry.save() is False  # False means updated existing

    res = entry.collection.find_one({"title": title})
    assert res is not None
    assert entry["textBody"] == "this is the NEW text"

    # check entry _id NOT added again into diary's entries array
    diary = Diary({"_id": D_ID})
    diary.reload()
    count = 0
    for id in diary["entries"]:
        if (id == res["_id"]):
            count = count + 1
    assert count == 1


def test_entry_reload_no_id():
    entry = Entry()
    assert entry.reload() is False


def test_entry_reload_bad_id():
    entry = Entry({"_id": ObjectId()})
    assert entry.reload() is False


def test_entry_reload():
    title = "test_find_entry_in_diary_found"
    from_db = Entry.collection.find_one({"title": title})
    assert from_db is not None
    id = str(from_db["_id"])
    entry = Entry({"_id": id})
    assert entry.reload() is True
    for item in from_db:
        assert item in entry
        if item == "_id":
            assert str(from_db[item]) == entry[item]
        else:
            assert from_db[item] == entry[item]


def test_entry_remove_no_diary():
    entry = Entry()
    assert entry.remove() is None


def test_entry_remove_bad_diary():
    # get valid entry _id
    title = "test_new_entry_with_diary"
    from_db = Entry.collection.find_one({"title": title})
    assert from_db is not None
    id = str(from_db["_id"])

    entry = Entry({"_id": id, "d_id": ObjectId()})
    assert entry.remove() is None


def test_entry_remove_no_id():
    entry = Entry({"d_id": D_ID})
    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    assert diary is not None
    num = len(diary["entries"])
    assert entry.remove() is None
    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    num2 = len(diary["entries"])
    assert num == num2


def test_entry_remove_bad_id():
    entry = Entry({"d_id": D_ID, "_id": str(ObjectId())})
    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    assert diary is not None
    num = len(diary["entries"])
    assert entry.remove() is None
    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    num2 = len(diary["entries"])
    assert num == num2


def test_entry_remove_valid():
    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    assert diary is not None
    num = len(diary["entries"])

    title = "test_new_entry_with_diary"
    doc = Entry.collection.find_one({"title": title})
    assert doc is not None
    id = doc['_id']
    assert id in diary["entries"]

    entry = Entry({"d_id": D_ID, "_id": str(id)})
    res = entry.remove()
    assert res is not None
    assert res.deleted_count == 1

    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    num2 = len(diary["entries"])
    assert num == (num2 + 1)
    assert id not in diary["entries"]


def test_entry_remove_2():
    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    assert diary is not None
    num = len(diary["entries"])

    title = "test_find_entry_in_diary_found"
    from_db = Entry.collection.find_one({"title": title})
    assert from_db is not None
    id = from_db["_id"]
    assert id in diary["entries"]

    entry = Entry({"_id": str(id), "d_id": D_ID})
    res = entry.remove()
    assert res is not None
    assert res.deleted_count == 1

    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    num2 = len(diary["entries"])
    assert num == (num2 + 1)
    assert id not in diary["entries"]


def test_end():
    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    assert diary is not None
    assert len(diary["entries"]) == 0
    assert Entry.collection.find_one({}) is None

    # set references back to main db
    Entry.dbStr = Diary.dbStr = "myDiaryApp"
    Entry.db = Entry.cluster[Entry.dbStr]
    Entry.collection = Entry.db["entries"]
    Diary.db = Diary.cluster[Diary.dbStr]
    Diary.collection = Diary.db["diaries"]


# def test_find_all_diaries():
#     num_diaries = len(d_collection.find())
#     diaries = Diary().find_all()
#     assert num_diaries == len(diaries)
