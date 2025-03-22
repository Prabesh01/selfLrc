from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Song
import re
from .utils import update_lyrics
from django.utils.translation import gettext_lazy as _
from asgiref.sync import async_to_sync

def view_perm_check(request):
    return request.user.is_superuser

class UserAdmin(UserAdmin):    
    list_display = ("username", "date_joined", "last_login",)

    def has_add_permission(self, request):
        return view_perm_check(request)

    def has_view_permission(self, request, obj=None):
        return view_perm_check(request)

    def has_change_permission(self, request, obj=None):
        return view_perm_check(request)
        
    def has_delete_permission(self, request, obj=None):
        return view_perm_check(request)

def perm_check(request, obj):
    if obj:
        return request.user.is_superuser or request.user == obj.user
    else: return request.user.is_superuser

class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'lyrics_db', 'delay')
    readonly_fields = ('get_lyrics_text',) 
    search_fields = ['title','updated_title']
    fieldsets = (
        (None, {
            'fields': ('title', 'updated_title', 'lyrics_id', 'lyrics_db', 'delay', 'custom_lyrics', 'get_lyrics_text','user',)
        }),
    )

    def save_model(self, request, obj, form, change):
        title=obj.title
        if obj.updated_title:
            title=obj.updated_title
        title_pattern = r'^(.*?) - (.*?)$'
        match = re.match(title_pattern, title)

        if match:
            name, artist = match.groups()
            # if not obj.lyrics_db:
            if 'updated_title' in form.changed_data:
                # update_lyrics(name.strip(), artist.strip(), obj)
                async_to_sync(update_lyrics)(name.strip(), artist.strip(), obj)

        else:
            self.message_user(request, _("Invalid Title Format!"), level='error')
            return

        super().save_model(request, obj, form, change)


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(user=request.user)
        return qs
    
    def has_add_permission(self, request, obj=None):
        return True if request.user.is_superuser else False

    def has_change_permission(self, request, obj=None):
        return perm_check(request, obj)            

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True        
        if obj:
            return request.user == obj.user
        return True if self.get_queryset(request).exists() else False
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += ("user","title",)
        return readonly_fields
    
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Song, SongAdmin)