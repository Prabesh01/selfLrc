from django.db import models
from django.contrib.auth.models import User

class Song(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, help_text="name - artist [album]")
    updated_title= models.CharField(max_length=150, help_text="name - artist [album]", blank=True, null=True)
    lyrics_id = models.CharField(max_length=50, blank=True, null=True)
    lyrics_db = models.IntegerField(help_text="null: not found, 0: custom, 1: spotify, 2: lrclibrary, 3: textyl", blank=True, null=True)
    delay = models.IntegerField(default=0)
    custom_lyrics = models.TextField(blank=True, null=True)

    def get_lyrics_text(self):
        from .utils import get_local_lyrics
        return get_local_lyrics(self)    
    
    get_lyrics_text.short_description = 'Lyrics'
