from django.urls import path
from django.urls import include

from filestorage import views

from django.conf import settings
from django.conf.urls.static import static

#from django.contrib.auth import views as auth_views
#from filestorage.views import FolderListView

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.logoutView, name='logout'),
    path('data', views.AccessDataView.as_view()),
    path('upload', views.UploadFileView.as_view()),
    path('source', views.ProduceImageView.as_view()),
    path('comment', views.CommentView.as_view()),
    path('download', views.DownloadItemsView.as_view()),
    path('directory', views.CreateNewFolderView.as_view()),
    path('remove', views.DeleteItemView.as_view()),
    path('move', views.ReplaceItemsView.as_view()),
    path('share', views.ShareItemsView.as_view()),

    path('folder/<slug:folder_id>/', views.commonView, name='folder-view'),

] 
