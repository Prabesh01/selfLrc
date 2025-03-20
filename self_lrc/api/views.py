from app.utils import get_lyrics
import json
from django.http import HttpResponse
from django.contrib.auth.models import User
from app.models import Song


def search_songs(request, username):
    q=request.GET.get('q',None)
    track_name = request.GET.get('track_name',None)
    artist_name = request.GET.get('artist_name',None)
    album_name = request.GET.get('album_name',None)
    duration= request.GET.get('duration',None)
    return HttpResponse(json.dumps([{"trackName":"Turn up the Radio","artistName":"OK Go","albumName":"Hungry Ghosts","syncedLyrics":"[01:01.44] You know it's always just inches shy\n[01:05.02] So turn off the lights\n[02:54.22] "}]), content_type="application/json")

def clean_fname(name):
    if len(name.split('.')[-1])<5:
        return '.'.join(name.split('.')[:-1])
    return name

def get_songs(request, username):
    try:
        user = User.objects.get(username=username)
    except:
        return HttpResponse(json.dumps({"syncedLyrics":"[00:10.00] UnAuthorized!\n[00:15.00] Invalid User"}), content_type="application/json")

    track_name = clean_fname(request.GET.get('track_name',''))
    artist_name = clean_fname(request.GET.get('artist_name',''))
    album_name = clean_fname(request.GET.get('album_name',''))
    return HttpResponse(json.dumps({"syncedLyrics":get_lyrics(track_name,artist_name,album_name, user)}), content_type="application/json")