import pytest
import pymongo
from pymongo import MongoClient
from model_mongodb import *


# uri = 'mongodb+srv://client:mydiaryapp@cluster0-k792t.azure.mongodb.net/test?re\
#     tryWrites=true&w=majority'
# db = pymongo.MongoClient(uri)["myDiaryApp"]
# d_collection = db["diaries"]

# def test_find_all_diaries():
#     num_diaries = len(d_collection.find())
#     diaries = Diary().find_all()
#     assert num_diaries == len(diaries)

def test_diary_reload_DNE():
    diary = Diary()
    assert diary.reload() is False


def test_diary_reload_bad_id():
    diary = Diary({"_id": "bad id"})
    assert diary.reload() is False
