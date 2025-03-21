from django.apps import AppConfig
from django.db.models.signals import post_migrate

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import Song
        
        post_migrate.connect(self.setup_groups, sender=self)
        post_migrate.connect(self.create_superuser, sender=self)

    
    def setup_groups(self, sender, **kwargs):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import Song
        
        allow_group, created = Group.objects.get_or_create(name='allow')
        
        song_content_type = ContentType.objects.get_for_model(Song)
        
        song_permissions = Permission.objects.filter(
            content_type=song_content_type,
            codename__in=['change_song', 'delete_song', 'view_song']
        )
        
        for permission in song_permissions:
            allow_group.permissions.add(permission)
        
        if created:
            print("Created 'allow' group with Song permissions")
        else:
            print("Updated 'allow' group permissions")

    def create_superuser(self, sender, **kwargs):
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        if not User.objects.filter(username='admin').exists():
            try:
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='pass'
                )
                print("Superuser 'admin' created successfully")
            except Exception as e:
                print(f"Error creating superuser: {e}")
        else:
            print("Superuser 'admin' already exists")            