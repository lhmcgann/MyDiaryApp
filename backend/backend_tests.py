import pytest
import requests
from backend import *


def test_get_diaries_get():
    "GET request to url returns a 200"
    url = 'https://localhost:5000/diaries'
    req = requests.get(url)
    print(req)
