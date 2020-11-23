
# Create your views here.
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import requires_csrf_token
from django.views.decorators.csrf import ensure_csrf_cookie

from django.http import HttpResponseServerError

from django.contrib.auth.decorators import login_required

from django.contrib.auth import logout

import os, sys
import zlib
from zipfile import ZipFile, ZIP_STORED
from pathlib import Path
from PIL import Image
from datetime import datetime, timedelta
import tempfile
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseNotFound

from filestorage.models import File, Comment, Folder, DiskQuota, Share, Source
from django.contrib.auth.models import User

from django.core.files.images import ImageFile
from django.http import FileResponse

from django.contrib.auth import views as auth_views
from filestorage.forms import NewFolderNameForm, CommentForm
import json
# Create your views here.

@ensure_csrf_cookie
@login_required
def index(request):

    root = Folder.root(request.user)
    return HttpResponseRedirect(reverse('folder-view', args=[root.pk]))

class Login(auth_views.LoginView):

    template_name = 'registration/login.html'

def logoutView(request):

    logout(request)
    return HttpResponseRedirect(reverse('index'))              


from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin



def commonView(request, folder_id):

    if request.user.is_authenticated:
         
        if request.method == 'GET' and 's' in request.GET:
            share_id = request.GET['s']
            sh = Share.objects.get(pk=share_id)
            shared_folder = sh.addContent(request.user)
            return HttpResponseRedirect(reverse('folder-view', args=[shared_folder.pk]))
        else:
            # Gather permitted content     
            request.session['current_folder'] = folder_id
            try:
                folder = request.user.owner_folder_set.get(pk=folder_id)
                path_seq = folder.getChain()
            except Folder.DoesNotExist:
                return HttpResponseForbidden()
          
      
    else:
        # Anonymous user with share link
        if request.method == 'GET' and 's' in request.GET: 
            share_id = request.GET['s']
            request.session['share_id'] = share_id
            return HttpResponseRedirect(reverse('folder-view', args=[folder_id]))
        else:
            share_id = request.session.get('share_id')
            if share_id:
                try:
                    sh = Share.objects.get(pk=share_id)
                except Share.DoesNotExist:
                    return HttpResponseNotFound()

                folder = Folder.objects.get(pk=folder_id)
                path_seq = folder.getChain(sh)
                

                request.session['current_folder'] = folder_id
            else:
                return HttpResponseRedirect(reverse('login'))


    context = {
                'misc': {'owner': folder.owner.username},
                'path': path_seq,
    }
    return render(request, 'filestorage/index.html', context)
 

from django.views import View
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist 
from django.db.models import Q

from django.conf import settings

class FileStorageBaseView(View):
    """Sure user's request data has appropriate access rights."""
    """Restrict malicious access."""
    
    cwd = None      # Required overall in request
    share = None    # Required for non logged users with share link
    files = []
    folders = []
            
    def isProperAuthorisedAccess(self, request):
        if request.user.is_authenticated:
            try:
                # Get folder's contents in a Move menu
                if 'move_menu_folder_id' in request.POST:
                    folder_id = request.POST['move_menu_folder_id']
                elif 'current_folder' in request.session :
                    folder_id = request.session['current_folder']
                else:
                    raise KeyError("No a Folder's primary keys in a request are given.")    

                self.cwd = Folder.objects.get(pk=folder_id,
                                              owner=request.user )

            except (KeyError, ObjectDoesNotExist) as e:
                if settings.DEBUG:
                    raise Exception(e) 
                return False

            return True

        return False
            
    def isProperNonAuthorisedAccess(self, request):
        if 'current_folder' in request.session and 'share_id' in request.session:
            folder_id = request.session['current_folder']
            share_id = request.session['share_id']
            try:
                share = Share.objects.get(pk=share_id)
                self.share = share
                # Examine folder_id is share
                is_request_folder_share = share.folders.filter(pk=folder_id).exists()
                if is_request_folder_share or folder_id == share.origin.pk:
                    self.cwd = Folder.objects.get(pk=folder_id)
                else:
                    raise Folder.DoesNotExist(f"{folder_id} isn't shared.")                  
            except ObjectDoesNotExist as e:
                if settings.DEBUG:
                    raise Exception(e) 
                return False
            
            return True

        return False
        
    def getDecodedJson(self, request):
        decoded = {}
        decoded['files'] = []
        decoded['folders'] = []

        files_json = request.POST.get('files')
        folders_json = request.POST.get('folders')

        if files_json and folders_json:
            # Validate input
            try:
                decoded['files'] = json.loads(files_json)
                decoded['folders'] = json.loads(folders_json)
            except json.JSONDecodeError as e:
                if settings.DEBUG:
                    raise json.JSONDecodeError(e) 
                return None

            return decoded

        return None

    def setItemsNoAuthorized(self, request):
        share = self.share
        decoded_input = self.getDecodedJson(request)
      
        if decoded_input:
            files, folders = decoded_input.values()

            try:
                self.files = [File.objects.get(pk=id, file_share_set=share) for id in files]
                self.folders = [Folder.objects.get(pk=id, folder_share_set=share) for id in folders]
            except (File.DoesNotExist, Folder.DoesNotExist) as e: 
                raise ObjectDoesNotExist(e) 

    def setItems(self, request):
        user = request.user
        decoded_input = self.getDecodedJson(request)

      
        if decoded_input:
            files, folders = decoded_input.values()

            try:
                self.files = [File.objects.get(pk=id, folder=self.cwd) for id in files]
                self.folders = [Folder.objects.get(pk=id, owner=user) for id in folders]
            except (File.DoesNotExist, Folder.DoesNotExist) as e: 
                raise ObjectDoesNotExist("Selected files aren't belong user.")

    def getData(self, files=[], folders=[], share_mode=False):

        data = {}

        data['folders'] = []
        for f in folders:
            if share_mode:
                status = False
            else:
                status = f.isShare()
           
            data['folders'] += [
                                {
                                    'folder_id': f.pk,
                                    'folder_name': f.name,
                                    'folder_url': reverse('folder-view', args=[f.pk]),
                                    'is_share': status
                                }
            ]

        data['files'] = []
        for file in files:
            if share_mode:
                status = False
            else:
                status = file.isShare()

            data['files'] += [
                {
                    "file_id": file.pk,
                    "owner": file.contributor.username,
                    "name": file.name,
                    "size": file.getSize(),
                    "is_share": status,
                    "type": None,
                    "upload": None,
                    "create": None
                }
            ]

        

        return data 


class UploadFileView(FileStorageBaseView):
      
    def post(self, request, *args, **kwargs):
        try:
            if self.isProperAuthorisedAccess(request):
                uploaded_file = request.FILES['source']
                file = File.objects.createFile(uploaded_file, self.cwd, request.user)
                data = self.getData(files=[file])

                return JsonResponse(data)
            else:
                return HttpResponseBadRequest()
        except Exception as e:
            return HttpResponseBadRequest()
    

class AccessDataView(FileStorageBaseView):

    def post(self, request, *args, **kwargs):
        try:
            if self.isProperAuthorisedAccess(request):
                files_inside = self.cwd.getFiles()
                folders_inside = self.cwd.getFolders()
                share_mode = False
            elif self.isProperNonAuthorisedAccess(request):
                files_inside = self.cwd.getFiles(self.share)
                folders_inside = self.cwd.getFolders(self.share)
                share_mode = True
            else:
                return HttpResponseForbidden()

            data = self.getData(files_inside, folders_inside, share_mode) 
            
            return JsonResponse(data)

        except Exception as e:
            return HttpResponseBadRequest()

class DeleteItemView(FileStorageBaseView):
    """ Remove files."""
    def post(self, request, *args, **kwargs):
        try:
            if self.isProperAuthorisedAccess(request):
                self.setItems(request)
             
                for file in self.files: self.cwd.deleteFile(file)
                for folder in self.folders: self.cwd.deleteFolder(folder)

                #TODO: Invoke a method using cron
                Source.removeOwnerlessOriginalFiles()   

                return HttpResponse(status=204)
            
            return HttpResponseForbidden()

        except Exception as e:
            return HttpResponseBadRequest()

class ReplaceItemsView(FileStorageBaseView):

    def post(self, request, *args, **kwargs):
        try:
            if self.isProperAuthorisedAccess(request):
                self.setItems(request)

                if 'destination' in request.POST:
                    destination_id = request.POST['destination']
                    destination_folder = request.user.owner_folder_set.get(pk=destination_id)

                    if self.cwd.replace(destination_folder, self.files, self.folders):
                        return HttpResponse(status=200) 

            return HttpResponseBadRequest()

        except (ObjectDoesNotExist, Exception) as e:
            return HttpResponseForbidden()
    

class ShareItemsView(FileStorageBaseView):

    def post(self, request, *args, **kwargs):
        try:
            if self.isProperAuthorisedAccess(request) and 'share_mode' in request.POST:
                self.setItems(request)
                mode = request.POST['share_mode']

                if self.files or self.folders:
                    if mode == 'start':
                        # Date expire is set here
                        sh = Share.objects.create(contributor=request.user, origin=self.cwd)
                        sh.shareItems(self.files, self.folders)
                        link = request.get_host() + sh.getLink()
                        data = self.getData(self.files, self.folders)

                        return JsonResponse({'share_link': link,
                                             'items': data })        
                    if mode =='stop':
                        Share.shareRemove(request.user, self.files, self.folders)
                        data = self.getData(self.files, self.folders)

                        return JsonResponse({'status': 'Unshare complete.',
                                             'items': data })
           
            return HttpResponseBadRequest()
        except Exception as e:
            return HttpResponseForbidden()

  
class DownloadItemsView(FileStorageBaseView):

    def post(self, request, *args, **kwargs):
        try:
            if self.isProperAuthorisedAccess(request):
                self.setItems(request)
            elif self.isProperNonAuthorisedAccess(request):
                self.setItemsNoAuthorized(request)
            else:
                return HttpResponseBadRequest()

            tmp_directory = tempfile.gettempdir()    
            zip_name = Path(tmp_directory) / 'archive.zip'    
            
            with ZipFile(zip_name, mode='w', compression=ZIP_STORED) as myzip:
                self.cwd.setArchive(myzip,
                                    self.files,
                                    self.folders,
                                    self.share)
      
            return FileResponse(open(zip_name, 'rb'), as_attachment=True )         

        except Exception as e:
            return HttpResponseForbidden()

class CreateNewFolderView(FileStorageBaseView):

    def post(self, request, *args, **kwargs):
        try:
            if self.isProperAuthorisedAccess(request):
                name = request.POST.get('new_folder')
                form = NewFolderNameForm({'new_name': name})
                if form.is_valid():
                    new_folder_name = form.cleaned_data['new_name']    
                    current_folder = self.cwd
                    folder = current_folder.addNewFolder(new_folder_name)
                    data = self.getData(folders=[folder])

                    return JsonResponse(data)
            
            return HttpResponseBadRequest()

        except Exception as e:
            return HttpResponseBadRequest()


class CommentView(FileStorageBaseView):
    
    def getData(self, comments):
        data = {}
        data['comments'] = []

        for c in comments:
            data['comments'] += [
                {
                    "author": c.author_name,
                    "date": c.date.ctime(), 
                    "text": c.text
                }
            ]

        return data

    def post(self, request, *args, **kwargs):
        try:
            if self.isProperAuthorisedAccess(request):
                user=request.user
                name=request.user.username
            elif self.isProperNonAuthorisedAccess(request):
                user = None
                name="Anonymous"   
            else:
                return HttpResponseBadRequest()        
            
            try:
                file_pk = request.POST.get('file_id')
                file = File.objects.get(pk=file_pk)
            except (KeyError, ObjectDoesNotExist) as e:
                if settings.DEBUG:
                    raise ObjectDoesNotExist(f"No file {file_pk} to comment.") 
                return HttpResponseForbidden()   

            
            text = request.POST.get('comment')
            form = CommentForm({'text': text})
            aliases = file.shared.all()
            if form.is_valid(): 
                # Create a new comment for all shared
                comment_text = form.cleaned_data['text']
                c = Comment.objects.create(file_id=file.pk,
                                            text=comment_text,
                                            user=user,
                                            author_name=name)
                for a in aliases: 
                    c = Comment.objects.create(file_id=a.pk,
                                            text=comment_text,
                                            user=user,
                                            author_name=name)

            # Get associated comments    
            comments = Comment.objects.filter(file_id=file_pk)
            data = self.getData(comments)
                
            return JsonResponse(data)

        except Exception as e:
            return HttpResponseForbidden()


class ProduceImageView(View):

    file = None
    response = HttpResponseForbidden()

    def validate(self, request, key):

        file_id = request.GET[key]

        if 'current_folder' not in request.session:
            if settings.DEBUG:
                raise Exception("There is no session 'current_folder' arg.")
            return False

        current_folder_id = request.session['current_folder']

        try:
            if request.user.is_authenticated:
                self.file = File.objects.get(pk=file_id,
                                             folder__pk=current_folder_id,
                                             contributor=request.user
                                             )
            elif 'share_id' in request.session:
                share_id = request.session['share_id']
                self.file = File.objects.get(pk=file_id,
                                             file_share_set__pk=share_id,
                                             folder__pk=current_folder_id)
            else:
                raise Exception("Access denied.")

        except File.DoesNotExist as e:
            if settings.DEBUG:
                raise ObjectDoesNotExist(f"Access denied to {file_id}") 
            return False
        
    def getModalImage(self, request):
        """Output a middle resolution for a modal element."""
        self.validate(request, 'm')
        size = (1000, 1000)
        try:
            file = self.file.getOriginFile()
            with Image.open(file) as im:
                im = im.convert('RGB')
                im.thumbnail(size)
                response = HttpResponse(content_type='image/jpeg')
                im.save(response, "JPEG")
                self.response = response
        except OSError:
            pass

    def getOriginal(self, request):

        self.validate(request, 'i')
        self.response = FileResponse(self.file.getOriginFile(), as_attachment=True)

    def getThumbnail(self, request):
        
        self.validate(request, 't')
        self.response = FileResponse(self.file.getThumbnail(), as_attachment=True)

    def get(self, request, *args, **kwargs):

        try:
            if 'i' in request.GET:
                self.getOriginal(request)
            elif 'm' in request.GET:
                self.getModalImage(request)
            elif 't' in request.GET:
                self.getThumbnail(request)
        except Exception as e:
            return HttpResponseForbidden()
       
        return self.response

