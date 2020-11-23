from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.
from filestorage.models import File, Comment, Folder, DiskQuota, Share



class DiskQuotaInline(admin.TabularInline):
    model = DiskQuota
    extra = 0
    can_delete = False
    fields = [('used', 'limit')]
    
class FolderInline(admin.TabularInline):
    model = Folder
    extra = 0
    can_delete = False
    verbose_name_plural = 'folders'

    fields = [('id', 'name', 'path')]

# Re-register UserAdmin
admin.site.unregister(User)

# Define a new User admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (DiskQuotaInline, FolderInline)

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'path', 'name')
    list_filter = ('owner',)
