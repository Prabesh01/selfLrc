from app.utils import get_lyrics
import json
from django.http import HttpResponse
from django.contrib.auth.models import User
from app.models import Song
from random import randint

temp={}

def search_songs(request, username):
    global temp
    try:
        user = User.objects.get(username=username)
    except:
        return HttpResponse(json.dumps([{"trackName":'N/A',"artistName":'N/A',"albumName":'N/A',"syncedLyrics":"[00:10.00] UnAuthorized!\n[00:15.00] Invalid User"}]), content_type="application/json")

    q=clean_fname(request.GET.get('q',''))
    track_name = clean_fname(request.GET.get('track_name',''))
    artist_name = clean_fname(request.GET.get('artist_name',''))
    album_name = clean_fname(request.GET.get('album_name',''))
    duration = request.GET.get('duration','0')
    if not q and not track_name:
        return HttpResponse(json.dumps([]), content_type="application/json")
    if q:
        track_name=q
    lrc=get_lyrics(track_name,artist_name, user)
    if lrc=="tryAgain":
        return HttpResponse(json.dumps([]), content_type="application/json")  
    if lrc=="NotFound":
        # if not 'poweramp' in request.META.get('HTTP_USER_AGENT', 'Unknown').lower():
        return HttpResponse(json.dumps([]), content_type="application/json")      
        # lrc="[00:10.00] :(\n[00:15.00] Not Found"
    lid=str(randint(0,5555))
    tosend=[{"id":lid, "name":track_name, "duration":int(duration), "instrumental":False, "plainLyrics":"", "trackName":track_name,"artistName":artist_name,"albumName":album_name, "syncedLyrics":lrc}]
    temp[lid]=tosend[0]
    return HttpResponse(json.dumps(tosend), content_type="application/json")

def clean_fname(name):
    if '.' in name and len(name.split('.')[-1])<5:
        return '.'.join(name.split('.')[:-1])
    return name

def get_lyrics_id(request, username, lid):
    global temp
    lrc=temp[str(lid)]
    if len(temp)>50:
        temp={}
    return HttpResponse(json.dumps(lrc), content_type="application/json")

def get_songs(request, username):
    try:
        user = User.objects.get(username=username)
    except:
        return HttpResponse(json.dumps({"syncedLyrics":"[00:10.00] UnAuthorized!\n[00:15.00] Invalid User"}), content_type="application/json")

    track_name = clean_fname(request.GET.get('track_name',''))
    artist_name = clean_fname(request.GET.get('artist_name',''))
    album_name = clean_fname(request.GET.get('album_name',''))
    if not track_name:
        return HttpResponse(json.dumps({"message":"Track name not specified","name":"TrackNotProvided","statusCode":404}), content_type="application/json")
    lrc=get_lyrics(track_name,artist_name, user)
    if lrc=="tryAgain":
        return HttpResponse(json.dumps({"message":"Failed to find specified track","name":"TrackNotFound","statusCode":404}), content_type="application/json")        
    if lrc=="NotFound":
        lrc="[00:10.00] :(\n[00:15.00] Not Found"
    return HttpResponse(json.dumps({"syncedLyrics":lrc}), content_type="application/json")


