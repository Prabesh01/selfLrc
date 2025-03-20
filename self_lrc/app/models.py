from django.db import models
from .utils import get_lyrics
from django.contrib.auth.models import User

class Song(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, help_text="artist - name [album]")
    updated_title= models.CharField(max_length=50, help_text="artist - name [album]", blank=True, null=True)
    lyrics_id = models.CharField(max_length=50, blank=True, null=True)
    lyrics_db = models.IntegerField(help_text="0: custom, 1: spotify, 2: lrclibrary, 3: textyl", blank=True, null=True)
    delay = models.IntegerField(default=0)
    custom_lyrics = models.TextField(blank=True, null=True)

    def get_lyrics_text(self):
        return get_lyrics(self.title)    
    
    get_lyrics_text.short_description = 'Lyrics'