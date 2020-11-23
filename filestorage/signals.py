
from django.contrib.auth.models import User
#from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from filestorage.models import Folder


@receiver(post_save, sender=User)
def create_user_root_folder(sender, instance, created, **kwargs):
    """Create root folder for a new user"""
    if created:
        Folder.objects.create(owner=instance)
        #TODO: Define user quota
       
