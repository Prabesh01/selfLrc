from app.utils import get_lyrics
import json
from django.http import HttpResponse

def search_songs(request, username):
    # read get parameters
    q=request.GET.get('q',None)
    track_name = request.GET.get('track_name',None)
    artist_name = request.GET.get('artist_name',None)
    album_name = request.GET.get('album_name',None)
    tosend=''
    if q: tosend=q
    else:
        if track_name: tosend=track_name
        if artist_name: tosend+=f' - {artist_name}'
        if album_name: tosend+=f' [{album_name}]'
    if not tosend:
        return HttpResponse(json.dumps([]), content_type="application/json")
    return HttpResponse(json.dumps([{"syncedLyrics":get_lyrics(tosend)}]), content_type="application/json")