from app.utils import get_lyrics
import json
from django.http import HttpResponse
from django.contrib.auth.models import User
from app.models import Song


def search_songs(request, username):
    try:
        user = User.objects.get(username=username)
    except:
        return HttpResponse(json.dumps([{"trackName":'N/A',"artistName":'N/A',"albumName":'N/A',"syncedLyrics":"[00:10.00] UnAuthorized!\n[00:15.00] Invalid User"}]), content_type="application/json")

    q=clean_fname(request.GET.get('q',''))
    track_name = clean_fname(request.GET.get('track_name',''))
    artist_name = clean_fname(request.GET.get('artist_name',''))
    album_name = clean_fname(request.GET.get('album_name',''))
    if not q and not track_name:
        return HttpResponse(json.dumps([]), content_type="application/json")
    if q:
        track_name=q
    lrc=get_lyrics(track_name,artist_name,album_name, user)
    if lrc=="tryAgain":
        return HttpResponse(json.dumps([]), content_type="application/json")        
    return HttpResponse(json.dumps([{"trackName":track_name,"artistName":artist_name,"albumName":album_name, "syncedLyrics":lrc}]), content_type="application/json")

def clean_fname(name):
    if '.' in name and len(name.split('.')[-1])<5:
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
    lrc=get_lyrics(track_name,artist_name,album_name, user)
    if lrc=="tryAgain":
        return HttpResponse(json.dumps({"message":"Failed to find specified track","name":"TrackNotFound","statusCode":404}), content_type="application/json")        
    return HttpResponse(json.dumps({"syncedLyrics":lrc}), content_type="application/json")