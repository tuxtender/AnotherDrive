from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from django.urls import reverse

from PIL import Image
import zlib
import tempfile
from pathlib import Path
from django.conf import settings

from django.core.exceptions import ObjectDoesNotExist

from filestorage.misc import generate_uuid, convert_size, generate_token
from django.db.models import Q

from django.urls import reverse

from datetime import datetime, timedelta
# Create your models here.


class DiskQuota(models.Model):
    """Model representing a disk limit for user."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    limit = models.BigIntegerField()
    used = models.BigIntegerField()

    @staticmethod
    def getSizeOfSelected(files=[], folders=[], share=None):

        size = 0
        for f in files: size += f.original.item.size
        for d in folders:
            nfs = d.getNestedFiles()
            if share:
                nfs = nfs.filter(file_share_set=share)
            for nf in nfs:
                size += nf.original.item.size
        return size

    @staticmethod
    def convert_size(size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)

        return "%s %s" % (s, size_name[i])
    
    def __str__(self):
        u = convert_size(self.used)
        a = convert_size(self.limit)
        return f"{self.user} used {u} (Limit is {a})"   


class SourceManager(models.Manager):

    def createSource(self, key, uploaded_file):

        src = Source.objects.create(id=key, item=uploaded_file)
        self.__makeThumbnail(src)

        return src

    @staticmethod
    def __makeThumbnail(src):

        #image_not_available = static('filestorage/images/image_not_available.jpg')
        thumbnail_name = str(src.id) + ".jpg"
        size = (300, 300)

        with tempfile.TemporaryFile() as fp:
            try:
                with Image.open(src.item) as im:
                    rgb_im = im.convert('RGB')
                    rgb_im.thumbnail(size)
                    rgb_im.save(fp, "JPEG")
                    src.img.save(thumbnail_name, fp)
            except OSError:
                pass
                #file.img.save(thumbnailName, image_not_available)



class Source(models.Model):
 
    id = models.CharField(primary_key=True, max_length=8)
    item = models.FileField(upload_to='uploads/')
    img = models.ImageField(upload_to='pic/', null=True)

    objects = SourceManager()

    @staticmethod
    def removeOwnerlessOriginalFiles():
        # Clear orphan files from File
        orphans = Source.objects.filter(file=None)
       
        for f in orphans:
            try:
                infile = Path(settings.MEDIA_ROOT) / f.item.name
                outfile = Path(settings.MEDIA_ROOT) / "trash" / Path(f.item.name).name
                infile.replace(outfile)

                inpic = Path(settings.MEDIA_ROOT) / f.img.name
                inpic.unlink(missing_ok=True)
            except Exception as e:
                if settings.DEBUG:
                    raise Exception(e) 
                
        orphans.delete()

    def __str__(self):
        return f"{self.id}"   


class FileManager(models.Manager):

    def createFile(self, uploaded_file, folder, user):

        hash = self.__checksum(uploaded_file)
        
        qs = Source.objects.filter(pk=hash) # Check existence
        if not qs.exists():
            origin_file = Source.objects.createSource(hash, uploaded_file)
            new_file = self.create(original=origin_file,
                                   name=uploaded_file.name,
                                   path=folder.full_name,
                                   contributor=user)
            folder.addFile(new_file)

            return new_file
        else:
            already_exist_item = qs.get()
            new_file = self.create(original=already_exist_item, name=uploaded_file.name, path=folder.full_name, contributor=user)
            folder.addFile(new_file)

            return new_file


    @staticmethod
    def __checksum(file):

        hash = 0
        for chunk in file.chunks():
            hash = zlib.crc32(chunk, hash)

        return hash


class File(models.Model):

    id = models.CharField(primary_key=True, default=generate_token, max_length=8)
    original = models.ForeignKey(Source, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    path = models.CharField(max_length=512)
    contributor = models.ForeignKey(User, on_delete=models.CASCADE)
    shared = models.ManyToManyField('self')

    objects = FileManager()

    @property
    def full_name(self):
        
        if self.path == '/':
            return '/' + self.name
        return self.path + '/' + self.name
       
    def getSize(self):

        return self.original.item.size

    def getOriginalName(self):

        return self.original.item.name

    def getOriginalThumbnailName(self):

        return self.original.img.name

    def getThumbnail(self):

        return self.original.img

    def getOriginFile(self):

        return self.original.item

    def setPath(self, folder):

        self.path = folder.full_name
        self.save()
        return self.path

    def getPath(self):

        return self.path

    def isShare(self):
        """Check a share status."""
        # Suggest a file is unique over all users assets.
        # No duplicate allowed.
        qs = File.objects.filter(file_share_set=None, pk=self.pk)
        if qs.exists():
            return False
        return True

    def __str__(self):
        return f"{self.id} ({self.getOriginalName()})"   


class Folder(models.Model):

    id = models.CharField(primary_key=True, max_length=32, default=generate_uuid)
    files = models.ManyToManyField(File, blank=True)
    name = models.CharField(max_length=32, default="")
    path = models.CharField(max_length=512, default="")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='childs')
    size = models.BigIntegerField(null=True, default=None)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_folder_set')

    @staticmethod
    def root(user):

        return Folder.objects.get(owner=user, parent=None, name="")

    def parents(self):
        l = []
        p = self.parent
        while p:
            l += [p]
            p = p.parent
        return l

    def children(self):

        return self.childs.all()
    
    def setParent(self, folder):

        self.parent = folder
        self.save() 
        self.recalculatePath()      

    @property
    def full_name(self):
        "Get a full name of folder sort of /path/name."
        #self.recalculatePath()
        if self.path == '/':
            return '/' + self.name
        return self.path + '/' + self.name
    
    def recalculatePath(self):
        
        path_list = [p.name for p in self.parents() if p.name] # Root folder is ""
        path_list.reverse()
        path = '/'.join(path_list) # May be a/b/c or ""
        if path:
            self.path = '/' + path
        else:
            self.path = '/'
        self.save()

    def recalculateSize(self):
        size = 0
        for nf in self.getNestedFiles():
            size += nf.original.item.size
        self.size = size
        self.save()
        return size
 
    
    def getChain(self, share=None):
        """Path sequence of parent items include a current."""
        l = [self]
        l += self.parents()
        if share:
            n = [] 
            for i in l:
                if share.origin == i:
                    break
                n += [i]
            n += [share.origin]
            n.reverse()
            return n

        l.reverse()
        return l


    @staticmethod
    def __traverse(folder, share=None):
        #folder.recalculatePath()
        if not folder.getFiles() and not folder.getFolders():
            return

        for file in folder.getFiles(share):
            file.setPath(folder)
        
        for child in folder.getFolders(share):
            child.recalculatePath()
            Folder.__traverse(child)

    
    def replace(self, destination_folder, files=[], folders=[]):

        if self == destination_folder:
            return False
        
        # Validate selection
        for folder in folders:
            if destination_folder == folder.parent or folder.__isAncestor(destination_folder):
                if settings.DEBUG:
                    raise Exception("Attempt corrupt layout structure.") 
                return False 

        # Name conflict resolve
        children_name_list = [f.name for f in destination_folder.getFolders()]

        for folder in folders:
            folder_name = folder.name
            while folder_name in children_name_list:
                folder_name = '_' + folder_name
            else:
                folder.name = folder_name
                folder.save()
                
            folder.setParent(destination_folder)
            Folder.__traverse(destination_folder)

        for file in files:
            folder_of_selected_file = file.folder_set.get(owner=self.owner)
            if folder_of_selected_file != destination_folder:
                self.files.remove(file)
                destination_folder.addFile(file)
                file.setPath(destination_folder)
            else:
                return False

        return True

    def __isAncestor(self, item):

        if self in item.getChain():
            return True
        return False        

    def deleteFile(self, file):
        """It suggests no duplicate in user's folders"""
        file.delete()

    def deleteFolder(self, folder):

        nested_files = self.getNestedFiles()
        nested_files.delete() 
        folder.delete()

    def getNestedFolders(self, share=None):

        mask = self.full_name
        qs = Folder.objects.filter(owner=self.owner, path__startswith=mask)
        if share:
            qs = qs.filter(folder_share_set=share)
        
        return qs

    def getNestedFiles(self, share=None):

        mask = self.full_name
        qs = File.objects.filter(contributor=self.owner, path__startswith=mask) 
        if share:
            qs = qs.filter(file_share_set=share)

        return qs.distinct()

    def getFiles(self, share=None):

        files = self.files.all()
        if share:
            files = files.filter(file_share_set=share)
            
        return files   
    
    def getFolders(self, share=None):

        childs = self.children()
        if share:
            childs = childs.filter(folder_share_set=share)
        return childs
    
    
    def addNewFolder(self, new_name):
        new_path = self.full_name

        # Name conflict resolve
        while new_name in [f.name for f in self.getFolders()]:
            new_name = '_' + new_name

        folder = Folder.objects.create(owner=self.owner,
                                    name=new_name,
                                    parent=self,
                                    path=new_path)

        return folder

    def addFile(self, file):

        self.files.add(file)

   
    def setArchive(self, archive, files=[], folders=[], share=None):

        for f in files:
            archive_filename = f.name
            input = Path(settings.MEDIA_ROOT) / f.getOriginalName()
            archive.write(input, archive_filename)

        for d in folders:
            nfs = d.getNestedFiles(share)
            for nf in nfs:
                archive_filename = Path(nf.full_name).relative_to(d.path)
                input = Path(settings.MEDIA_ROOT) / nf.getOriginalName()
                archive.write(input, archive_filename)


    def isShare(self):
        """Check a share status."""
        # Suggest a folder is unique.
        # Query all item not in Share
        qs = Folder.objects.filter(folder_share_set=None, pk=self.pk)
        if qs.exists():
            return False
        return True          

    def __str__(self):
        return f"{self.pk}"

class Comment(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)
    author_name = models.CharField(max_length=150)
    date = models.DateTimeField(auto_now=True)
    text = models.CharField(max_length=200)

    class Meta:
        ordering = ['-date']
  
    def __str__(self):
        return f"{self.author_name} {self.text} "

class Share(models.Model):
    id = models.CharField(primary_key=True, max_length=32, default=generate_uuid, editable=False)
    contributor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributor_share_set')
    folders = models.ManyToManyField(Folder, related_name='folder_share_set')
    files = models.ManyToManyField(File, related_name='file_share_set')
    origin = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='origin_share_set')
    date = models.DateTimeField(auto_now_add=True)
    expire = models.DateTimeField(default=None, null=True)

    @staticmethod
    def shareRemove(user, files=[], folders=[]):
        """Stop sharing."""
        shares = user.contributor_share_set.all()
        for sh in shares:
            for file in files: sh.files.remove(file)
            for folder in folders:
                nd = folder.getNestedFolders()
                sh.folders.remove(*nd)
                sh.folders.remove(folder)
                nf = folder.getNestedFiles()
                sh.files.remove(*nf)
        #TODO: Invoke using cron
        Share.removeOrphanShares()

    @staticmethod
    def removeOrphanShares():

        qs1 = Share.objects.filter(folders=None)
        qs2 = Share.objects.filter(files=None)
     
        qs1.delete()
        qs2.delete()


    def shareItems(self, files=[], folders=[]):
        """Share files and folders."""
        for file in files: self.files.add(file)
        for folder in folders:
            self.folders.add(folder)
            files_in_current_folder = folder.getFiles()
            self.files.add(*files_in_current_folder)

            nested_folders = folder.getNestedFolders()
            for nf in nested_folders:
                self.folders.add(nf)
                nested_files = nf.getFiles()
                self.files.add(*nested_files)

        return self.getLink()


    def getLink(self):

        link = reverse('folder-view', args=[self.origin.pk]) + '?' + 's=' + self.id
        return link

    def getOriginFolder(self):

        return self.origin

    @staticmethod
    def cleanOverdue():

        now = datetime.now()
        Share.objects.filter(expire__gt=now).delete()

    def addContent(self, user):
        
        new_name_added_folder = ' '.join([self.contributor.username,
                                     self.date.ctime()])

         # Create a new folder is provided by a share link content 
        root = Folder.root(user)
        container = root.addNewFolder(new_name_added_folder)

        self.__folderTraverse(self.origin, user, container)

        return container
    
    
    def __folderTraverse(self, folder, user, prev_folder):
        
        if not folder.getFiles() and not folder.getFolders():
            return
        
        for f in folder.getFiles(share=self):
            new_file = File.objects.create(original=f.original,
                                               name=f.name,
                                               path=prev_folder.full_name,
                                               contributor=user)
            prev_folder.addFile(new_file)

            f.shared.add(new_file)

        for child in folder.getFolders(share=self):
            new_name = child.name
            if not new_name:
                new_name = self.contributor.username
    
            new = Folder.objects.create(owner=user,
                                        name=new_name,
                                        parent=prev_folder)
            new.recalculatePath()
            self.__folderTraverse(child, user, new)
    

    def __str__(self):
        return f"{self.id} {self.contributor}"
