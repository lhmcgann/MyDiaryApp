import pytest
import pymongo
from bson import ObjectId
from model_mongodb import *


# the ObjectId of the main diary in the tests collection
D_ID = "5ececfbc28f47f5e4408ca45"
# the ObjectId of the diary in the tests collection with the Sorted entries
SORT_D_ID = '5edc4ef620ac8950a849d3a4'
NUM_ENTRIES = 5


def test_setup():
    # enter "test mode": use testing db
    Entry.dbStr = Diary.dbStr = Tag.dbStr = "tests"
    Entry.db = Entry.cluster[Entry.dbStr]
    Entry.collection = Entry.db["entries"]
    Diary.db = Diary.cluster[Diary.dbStr]
    Diary.collection = Diary.db["diaries"]
    Tag.db = Tag.cluster[Tag.dbStr]
    Tag.collection = Tag.db["tags"]

    assert len(list(Entry.collection.find())) == NUM_ENTRIES
    assert Diary.collection.find_one({"_id": ObjectId(D_ID)}) is not None


def test_entry_gets_TEST():
    entry = Entry()
    clxns = entry.db.list_collection_names()
    expect = ["tests", "tags", "diaries", "entries"]
    for item in clxns:
        assert item in expect


def test_diary_gets_TEST():
    diary = Diary()
    clxns = diary.db.list_collection_names()
    expect = ["tests", "tags", "diaries", "entries"]
    for item in clxns:
        assert item in expect


def test_diary_save_new():
    doc = {"title": "test_diary_save_new", "entries": []}
    diary = Diary(doc)

    # before save, make sure not in db
    assert diary.collection.find_one({"title": "test_diary_save_new"}) is None

    diary.save()
    res = diary.collection.find_one({"title": "test_diary_save_new"})
    assert res is not None
    assert 'dateCreated' in res
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
    diary_model = {"_id": None, "entries": [], "title": ""}
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


def test_diary_remove_with_entries_tags():
    title = 'test_diary_remove_with_entries'
    diary = Diary({'title': title, 'entries': []})
    diary.save()
    assert diary.reload() is True
    did = diary['_id']

    e1 = Entry({'title': 'del diary 1', 'd_id': did, 'tags': []})
    e1.save()
    e2 = Entry({'title': 'del diary 2', 'd_id': did, 'tags': []})
    e2.save()
    t = Tag({'title': 'hi', 'd_id': did})
    t.save()

    diary.remove()
    assert diary.reload() is False
    assert Diary.collection.find_one({"title": title}) is None


def test_find_all_diaries():
    diaries = Diary().find_all()
    assert len(diaries) == 3


def test_find_by_title_diaries():
    diaries = Diary().find_by_title("Test 1")
    assert len(diaries) == 1
    assert diaries[0]['title'] == "Test 1"


def test_diary_get_entries():
    title = 'test_diary_get_entries'
    diary = Diary({'title': title, 'entries': []})
    diary.save()
    assert diary.reload() is True
    did = diary['_id']

    e1 = Entry({'title': 'get entries 1', 'd_id': did, 'tags': []})
    e1.save()
    e1.reload()
    e2 = Entry({'title': 'get entries 2', 'd_id': did, 'tags': []})
    e2.save()
    e2.reload()
    docs = [e1, e2]

    entries = diary.get_entries()
    assert entries == docs

    diary.remove()


def test_tag_get_diary():
    assert Tag().get_diary(Diary()) is None


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
    doc = {"title": title, "tags": [], "textBody": "nothing", "d_id": D_ID}
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
    assert 'dateCreated' in res
    assert isinstance(res["_id"], ObjectId)
    res['d_id'] = str(res['d_id'])
    for item in doc:
        assert item in res
        assert doc[item] == res[item]

    # check entry _id got into diary's entries array
    diary = Diary({"_id": D_ID})
    diary.reload()
    assert isinstance(diary["_id"], str)
    for e in diary["entries"]:
        assert isinstance(e, str)
    assert str(res["_id"]) in diary["entries"]


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
        if (id == str(res["_id"])):
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


def test_tag_find_by_title_bad_title():
    assert Tag().find_by_title("bad title", D_ID) is None


def test_tag_find_by_title_bad_did():
    assert Tag().find_by_title("valid title", ObjectId()) is None


def test_tag_find_by_title():
    tag = Tag().find_by_title("first tag", D_ID)
    assert tag is not None
    assert tag['title'] == "first tag"
    assert isinstance(tag["_id"], str)


def test_add_tag_no_eid():
    assert Entry().add_tag("valid tag") is False


def test_add_tag_bad_eid():
    assert Entry({"_id": str(ObjectId())}).add_tag("valid tag") is False


def test_add_tag_existing():
    e_doc = {"title": "test_add_tag", "tags": [], "d_id": D_ID,
             "textBody": "nada mucho"}
    entry = Entry(e_doc)
    entry.save()
    entry.reload()
    assert entry is not None
    assert "_id" in entry
    assert len(entry["tags"]) == 0

    tag_name = "valid tag"
    assert entry.add_tag(tag_name) is True
    assert len(entry["tags"]) == 1

    title = entry["tags"][0]
    tag = Tag({"title": title, 'd_id': entry['d_id']})
    assert tag.reload() is True
    assert tag["title"] == tag_name


def test_add_tag_new():
    title = "test_add_tag"
    res = Entry.collection.find({"title": title})
    assert res is not None
    id = str(res[0]["_id"])

    entry = Entry({"_id": id})
    entry.reload()
    assert isinstance(entry["_id"], str)
    assert len(entry["tags"]) == 1
    assert 'valid tag' in entry['tags']
    # for tag in entry["tags"]:
    #     assert isinstance(tag, str)

    tag_name = "new tag"
    entry.add_tag(tag_name)
    assert len(entry["tags"]) == 2
    assert 'new tag' in entry['tags']
    # for tag in entry["tags"]:
    #     assert isinstance(tag, str)
    tag = Tag().find_by_title(tag_name, entry.d_id)
    assert tag is not None
    assert "d_id" in tag


def test_save_tag_no_args():
    count = len(list(Tag.collection.find()))
    Tag().save()
    count2 = len(list(Tag.collection.find()))
    assert count == count2


def test_save_tag_bad_did():
    count = len(list(Tag.collection.find()))
    tag = Tag({'title': 'first tag', 'd_id': ObjectId()})
    tag.save()
    count2 = len(list(Tag.collection.find()))
    assert count == count2


def test_save_tag_old_id():
    before = Tag({'_id': '5edc2aab2d64f19e729bff38'})  # id of first tag
    before.reload()

    count = len(list(Tag.collection.find()))
    tag = Tag({'_id': '5edc2aab2d64f19e729bff38', 'title': 'wrong'})
    tag.save()
    tag.reload()
    count2 = len(list(Tag.collection.find()))
    assert count == count2
    assert tag != before
    assert tag['title'] == 'wrong'

    tag['title'] = 'first tag'
    tag.save()
    tag.reload()
    count2 = len(list(Tag.collection.find()))
    assert count == count2
    assert tag == before


def test_save_tag_old_title_did():
    before = Tag({'_id': '5edc2aab2d64f19e729bff38'})  # id of first tag
    before.reload()

    count = len(list(Tag.collection.find()))
    tag = Tag({'title': 'first tag', 'd_id': D_ID})
    tag.save()
    count2 = len(list(Tag.collection.find()))
    assert count == count2

    tag.reload()
    assert tag == before


def test_save_tag_new_title():
    count = len(list(Tag.collection.find()))
    tag = Tag({'title': 'test_save_tag_new_title', 'd_id': D_ID})
    tag.save()
    count2 = len(list(Tag.collection.find()))
    assert (count+1) == count2

    tag.reload()
    assert '_id' in tag
    assert isinstance(tag['_id'], str)

    tag.remove()  # cleanup


def test_reload_tag_no_args():
    assert Tag().reload() is False


def test_reload_tag_bad_id():
    assert Tag({'_id': ObjectId()}).reload() is False


def test_reload_tag_no_title():
    assert Tag({'d_id': D_ID}).reload() is False


def test_reload_tag_no_did():
    assert Tag({'title': 'valid tag'}).reload() is False


def test_reload_tag_bad_title():
    assert Tag({'title': 'bad tag title', 'd_id': D_ID}).reload() is False


def test_reload_tag_bad_did():
    assert Tag({'title': 'valid tag', 'd_id': ObjectId()}).reload() is False


def test_reload_tag():
    tag = Tag({"title": 'valid tag', 'd_id': D_ID})
    assert tag.reload() is True
    assert '_id' in tag
    id = tag['_id']
    assert isinstance(id, str)

    tag2 = Tag({'_id': id})
    assert tag2.reload() is True
    assert tag == tag2


def test_delete_tag_no_eid():
    assert Entry().delete_tag("valid tag") is False


def test_delete_tag_bad_eid():
    assert Entry({"_id": str(ObjectId())}).delete_tag("valid tag") is False


def test_delete_tag_dne():
    title = "test_add_tag"
    res = Entry.collection.find({"title": title})
    assert res is not None
    entry = Entry(res[0])
    assert entry.reload() is True
    assert len(entry["tags"]) == 2

    tag_name = "bad tag"
    assert Tag().find_by_title(tag_name, entry.d_id) is None
    assert entry.delete_tag(tag_name) is False
    assert len(entry["tags"]) == 2


def test_delete_tag():
    title = "test_add_tag"
    res = Entry.collection.find({"title": title})
    assert res is not None
    entry = Entry(res[0])
    assert entry.reload() is True
    assert len(entry["tags"]) == 2

    tag_name = "valid tag"
    assert Tag().find_by_title(tag_name, entry.d_id) is not None
    assert entry.delete_tag(tag_name) is True
    entry.reload()
    assert len(entry["tags"]) == 1
    assert Tag().find_by_title(tag_name, entry.d_id) is not None


def test_remove_tag_no_title():
    assert Tag({'d_id': D_ID}).remove() is None


def test_remove_tag_bad_title():
    assert Tag({'title': 'fake', 'd_id': D_ID}).remove() is -1


def test_remove_tag_no_did():
    assert Tag({'title': 'valid tag'}).remove() is None


def test_remove_tag_bad_did():
    assert Tag({'title': 'valid tag', 'd_id': ObjectId()}).remove() is -1


def test_remove_tag():
    title = "test_add_tag"
    res = Entry.collection.find({"title": title})
    assert res is not None
    entry = Entry(res[0])
    assert entry.reload() is True
    assert len(entry["tags"]) == 1

    tag_name = "new tag"
    tag = Tag({'title': tag_name, 'd_id': entry.d_id})
    assert tag.remove() == 1
    entry.reload()
    assert len(entry["tags"]) == 0
    assert Tag().find_by_title(tag_name, entry.d_id) is None

    assert entry.remove() is not None  # cleanup for testing


def test_has_tag_no_id():
    assert Entry().has_tag('valid tag') is None


def test_has_tag_false():
    entry = Entry({'title': 'test_has_tag', 'd_id': D_ID, 'tags': []})
    entry.save()
    assert entry.has_tag('valid tag') is False
    entry.remove()


def test_filter_tags():
    e1 = Entry({'title': 'e1', 'd_id': D_ID, 'tags': [], 'textBody': "na"})
    e1.save()
    e1.reload()
    e2 = Entry({'title': 'e2', 'd_id': D_ID, 'tags': [], 'textBody': "na2"})
    e2.save()
    e2.reload()

    e1.add_tag('t1')
    e1.reload()
    entries = [e1, e2]
    res = Entry.filter_with_tags(entries, ['t1'])
    assert len(res) == 1
    assert res[0] == e1

    t1 = Tag({'title': 't1', 'd_id': D_ID})
    t1.reload()
    t1.remove()
    e1.remove()
    e2.remove()


def test_sort_entries_no_id():
    assert Diary().sort_entries_by_date_created() == []


def test_sort_entries_bad_id():
    assert Diary({'_id': ObjectId()}).sort_entries_by_date_created() == []


def test_sort_entries_empty_diary():
    assert Diary({'_id': D_ID}).sort_entries_by_date_created() == []


# NOTE: reverse=False --> recent last order
def test_sort_entries_recent_last():
    diary = Diary({'_id': SORT_D_ID})
    sorted_entries = diary.sort_entries_by_date_created(False)
    assert sorted_entries != []
    assert sorted_entries[0]['title'] == "Sort Test 1"
    assert sorted_entries[1]['title'] == "Sort Test 2"
    assert sorted_entries[2]['title'] == "Sort Test 3"
    assert sorted_entries[3]['title'] == "Sort Test 4"
    assert sorted_entries[4]['title'] == "Text Search - hello"


def test_sort_entries_recent_first():
    diary = Diary({'_id': SORT_D_ID})
    sorted_entries = diary.sort_entries_by_date_created()
    assert sorted_entries != []
    assert sorted_entries[0]['title'] == "Text Search - hello"
    assert sorted_entries[4]['title'] == "Sort Test 1"
    assert sorted_entries[3]['title'] == "Sort Test 2"
    assert sorted_entries[2]['title'] == "Sort Test 3"
    assert sorted_entries[1]['title'] == "Sort Test 4"


def test_text_search_entries_no_id():
    assert Diary().search_entries_for_text("hello") == []


def test_text_search_entries_bad_id():
    assert Diary({'_id': ObjectId()}).search_entries_for_text("hello") == []


def test_text_search_entries_empty_diary():
    assert Diary({'_id': D_ID}).search_entries_for_text("hello") == []


def test_text_search_entries_not_found():
    diary = Diary({'_id': SORT_D_ID})
    assert diary.search_entries_for_text("dfkjgd;vnkgjdghjdkjgbdfkj") == []


def test_text_search_entries_found():
    diary = Diary({'_id': SORT_D_ID})
    entries = diary.search_entries_for_text("hello")
    assert len(entries) == 2
    e1 = Entry(list(Entry.collection.find({'title': "Sort Test 3"}))[0])
    e1 = e1.make_printable(e1)
    e2 = Entry(list(Entry.collection.find({'title': "Text Search - hello"}))[0])
    e2 = e2.make_printable(e2)
    assert (entries[0] == e1 or entries[0] == e2) is True
    assert (entries[1] == e1 or entries[1] == e2) is True


def test_end():
    diary = Diary.collection.find_one({"_id": ObjectId(D_ID)})
    assert diary is not None
    assert len(diary["entries"]) == 0
    assert len(list(Entry.collection.find())) == NUM_ENTRIES

    # set references back to main db
    Entry.dbStr = Diary.dbStr = Tag.dbStr = "myDiaryApp"
    Entry.db = Entry.cluster[Entry.dbStr]
    Entry.collection = Entry.db["entries"]
    Diary.db = Diary.cluster[Diary.dbStr]
    Diary.collection = Diary.db["diaries"]
    Tag.db = Tag.cluster[Tag.dbStr]
    Tag.collection = Tag.db["tags"]
