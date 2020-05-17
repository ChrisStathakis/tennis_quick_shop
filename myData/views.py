from django.shortcuts import render

from http import client
import urllib3
import requests

HOST = "www.domain.nl"
API_URL = "/api/url"


def test_get_view(request):
    url = 'http://127.0.0.10:3000/api/tables/tables-list/'
    r = requests.get(url, params={})
    books = r.json()
    print(books)
    return render(request, 'myData/home.html', context={'data': books['results']})


def test_post_view(request):
    url = ''