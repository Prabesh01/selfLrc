from django.db import models
from django.contrib.auth.models import User

class Song(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, help_text="name - artist")
    updated_title= models.CharField(max_length=150, help_text="name - artist", blank=True, null=True)
    lyrics_id = models.CharField(max_length=50, blank=True, null=True)
    lyrics_db = models.IntegerField(help_text="null: not found, 0: custom, 1: spotify, 2: lrclibrary, 3: textyl", blank=True, null=True)
    delay = models.IntegerField(default=0)
    custom_lyrics = models.TextField(blank=True, null=True)

    async def get_lyrics_text_async(self):
        from .utils import get_local_lyrics
        data = await get_local_lyrics(self)   
        return data
    
    def get_lyrics_text(self):
        """Synchronous wrapper for the async method"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_lyrics_text_async())
        finally:
            loop.close()
                
    get_lyrics_text.short_description = 'Lyrics'
