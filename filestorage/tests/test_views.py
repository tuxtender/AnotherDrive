from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from filestorage.models import File, Comment, Folder, DiskQuota, Share, Source
from filestorage import misc
from filestorage.views import index, AccessDataView
from django.core.files.base import ContentFile
import json
from io import BytesIO
# Create your tests here.

class IndexViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='dummy', password='top_secret')

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username='dummy')

    def test_non_authorized_user_access(self):
        """Redirect to login page with next redirect to index."""
        # Access to root url
        response = self.client.get('/')
        self.assertRedirects(response, '/login?next=/')

    def test_non_authorized_user_access_to_any_folder(self):
        """Redirect to login page in attempt malicious access."""
        folder = Folder.root(self.user)
        response = self.client.get(reverse('folder-view', args=[folder.pk]))
        self.assertRedirects(response, '/login')

    def test_authorized_user_access_to_own_exist_folder(self):
        folder = Folder.root(self.user)
        self.client.login(username='dummy', password='top_secret')
        response = self.client.get(reverse('folder-view', args=[folder.pk]))
        self.assertEqual(response.status_code, 200)

    def test_authorized_user_access_to_not_owned_exist_folder(self):
        """Forbidden access to not possessed folders."""
        another_user = User.objects.create_user(username='friend', password='top_secret')
        folder = Folder.root(another_user)
        self.client.login(username='dummy', password='top_secret')
        response = self.client.get(reverse('folder-view', args=[folder.pk]))
        self.assertEqual(response.status_code, 403)

    def test_authorized_user_access_to_index_page(self):
        """Redirect to root folder."""
        self.client.login(username='dummy', password='top_secret')
        response = self.client.get('/')
        root = Folder.root(self.user)
        self.assertRedirects(response, reverse('folder-view', args=[root.pk]))

    def test_non_authorized_user_access_with_share_link(self):
        
        folder = Folder.root(self.user)
        # Create and share folder at authorized user
        new_folder = folder.addNewFolder('new_folder')
        share = Share.objects.create(contributor=self.user, origin=new_folder)
        share.shareItems(folders=[folder])

        # First request set session variables and redirect 
        link = share.getLink()
        response = self.client.get(link)
        self.assertRedirects(response, reverse('folder-view', args=[share.origin.pk]))
        response = self.client.get(reverse('folder-view', args=[share.origin.pk]))
        self.assertEqual(response.status_code, 200)

    def test_non_authorized_user_access_with_not_valid_share_link_to_exist_folder(self):
        folder = Folder.root(self.user)
        new_folder = folder.addNewFolder('new_folder')
        not_valid_share_key = misc.generate_uuid()
        response = self.client.get(reverse('folder-view', args=[new_folder.pk]), {'s': not_valid_share_key})
        response = self.client.get(reverse('folder-view', args=[new_folder.pk]))
        self.assertEqual(response.status_code, 404)

    def test_authorized_user_get_valid_share_link(self):
        folder = Folder.root(self.user)
        new_folder = folder.addNewFolder('new_folder') 
        share = Share.objects.create(contributor=self.user, origin=new_folder)
        share.shareItems(folders=[folder])
        # First request set session variables and redirect 
        link = share.getLink()

        another_user = User.objects.create_user(username='friend', password='top_secret')
        self.client.login(username='friend', password='top_secret')
        response = self.client.get(link, follow=True)
        new_link, status = response.redirect_chain.pop()
        response = self.client.get(new_link)
        self.assertEqual(response.status_code, 200)

class AccessDataViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='dummy', password='top_secret')
        User.objects.create_user(username='friend', password='top_secret')

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(username='dummy')
        self.another_user = User.objects.get(username='friend')

        self.root_folder = Folder.root(self.user)

        self.folders = {}
        n0 = self.root_folder.addNewFolder('n0') # /n0
        self.folders['n0'] = n0
    
        self.files = {}
        f0 = ContentFile(b"dummy string f0")
        f0.name = 'f0'
        file_0 = File.objects.createFile(f0, self.root_folder, self.user)
        self.files['f0'] = file_0
     


    def test_authorized_user_access(self):
        """Authorized user fetch data"""
        self.client.login(username='dummy', password='top_secret')

        session = self.client.session
        session['current_folder'] = self.root_folder.pk
        session.save()

        response = self.client.post('/data') 
        expected_data = AccessDataView.getData(None,
                folders=[self.folders['n0']],
                files=[self.files['f0']]
                )
    
        self.assertJSONEqual(response.content, expected_data)


    def test_non_authorized_user_access_with_share_link(self):
        """Fetch share data with link without loggin."""
        sh = Share.objects.create(contributor=self.user, origin=self.root_folder)

        # Upload file that user not shared with other
        # they haven't displayed for non-authorized user with link
        n1 = self.root_folder.addNewFolder('n1') # /n1
        f1 = ContentFile(b"dummy string f1")
        f1.name = 'f1'
        File.objects.createFile(f1, self.root_folder, self.user)

        sh.shareItems(files=[self.files['f0']],
                      folders=[self.folders['n0']]
                      )
        
        session = self.client.session
        session['current_folder'] = self.root_folder.pk
        session['share_id'] = sh.pk
        session.save()

        response = self.client.post('/data') 
        expected_data = AccessDataView.getData(None,
                                               folders=[self.folders['n0']],
                                               files=[self.files['f0']],
                                               share_mode=True
                                               )
        # Shown only in Share recorded
        self.assertEqual(response.json(), expected_data)


    def test_authorized_user_try_fetch_data_from_not_own_folder(self):
        """Authorized user no fetch un possessed data."""
        self.client.login(username='friend', password='top_secret')

        session = self.client.session
        session['current_folder'] = self.root_folder.pk
        session.save()

        response = self.client.post('/data') 
        expected_data = b''
    
        self.assertEqual(response.content, expected_data)


    def test_non_authorized_user_try_fetch_data_exist_folder(self):
        """Non-authorized user no fetch any data."""
        session = self.client.session
        session['current_folder'] = self.root_folder.pk
        session.save()

        response = self.client.post('/data') 
        expected_data = b''
    
        self.assertEqual(response.content, expected_data)

class UploadFileViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='dummy', password='top_secret')
        self.another_user = User.objects.create_user(username='friend', password='top_secret')

        self.root_folder = Folder.root(self.user)

    def test_authorized_user_upload_file(self):
        """Authorized user upload file twice. Only aliases created."""
        self.client.login(username='dummy', password='top_secret')
        response = self.client.get(reverse('folder-view', args=[self.root_folder.pk]))
        self.assertEqual(response.status_code, 200)

        fp = BytesIO(b'dummy string f0')
        fp.name = "new file"

        response = self.client.post('/upload', {'source': fp})
        self.assertEqual(response.status_code, 200)

        count_of_original_file = Source.objects.all().count()
        self.assertEqual(count_of_original_file, 1)
        count_of_alias = File.objects.filter(name=fp.name).count()
        self.assertEqual(count_of_alias, 1)
        # Upload same file twice
        fp.seek(0)
        response = self.client.post('/upload', {'source': fp})
        self.assertEqual(response.status_code, 200)
        count_of_alias = File.objects.all().count()
        self.assertEqual(count_of_alias, 2)
        # Test there aren't duplicate
        count_of_original_file = Source.objects.all().count()
        self.assertEqual(count_of_original_file, 1)

    def test_authorized_user_upload_file_to_not_owned_folder(self):

        self.client.login(username='friend', password='top_secret')
    
        fp = BytesIO(b'dummy string f0')
        fp.name = "new file"
        session = self.client.session
        session['current_folder'] = self.root_folder.pk # Stranger's folder
        session.save()
        response = self.client.post('/upload', {'source': fp})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Source.objects.all().count(), 0)
        self.assertEqual(File.objects.all().count(), 0)

    def test_non_authorized_user_upload_file(self):

        fp = BytesIO(b'dummy string f0')
        fp.name = "new file"
        session = self.client.session
        session['current_folder'] = self.root_folder.pk # Stranger's folder
        session.save()
        response = self.client.post('/upload', {'source': fp})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Source.objects.all().count(), 0)
        self.assertEqual(File.objects.all().count(), 0)
   