from django.test import TestCase
from django.contrib.auth.models import User
from filestorage.models import File, Comment, Folder, DiskQuota, Share, Source
from django.core.files.base import ContentFile

class FolderModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='dummy', password='top_secret')

    def setUp(self):
        self.user = User.objects.get(username='dummy')
        # Root folder implicit created simultaneously a new user is added
        self.root_folder = Folder.root(self.user) 

    def test_folders_and_files_paths_changing_then_replace(self):

        # Create nested folders
        n0 = self.root_folder.addNewFolder('n0') # /n0
        self.assertEqual(n0.full_name, '/n0')
        n1 = n0.addNewFolder('n1') # /n0/n1
        self.assertEqual(n1.full_name, '/n0/n1')
        n2 = n1.addNewFolder('n2') # /n0/n1/n2
        self.assertEqual(n2.full_name, '/n0/n1/n2')
        n3 = n2.addNewFolder('n3') # /n0/n1/n2/n3
        self.assertEqual(n3.full_name, '/n0/n1/n2/n3')
        
        f3 = ContentFile(b"dummy string f3")
        f3.name = 'f3'
        file_3 = File.objects.createFile(f3, n3, self.user)
        self.assertEqual(file_3.full_name, '/n0/n1/n2/n3/f3')


        n3_1 = n2.addNewFolder('n3_1') # /n0/n1/n2/n3_1
        self.assertEqual(n3_1.full_name, '/n0/n1/n2/n3_1')
        n3_2 = n2.addNewFolder('n3_2') # /n0/n1/n2/n3_2
        self.assertEqual(n3_2.full_name, '/n0/n1/n2/n3_2')

        f3_2 = ContentFile(b"dummy string f3_2")
        f3_2.name = 'f3_2'
        file_3_2 = File.objects.createFile(f3_2, n3_2, self.user)
        self.assertEqual(file_3_2.full_name, '/n0/n1/n2/n3_2/f3_2')


        n1.replace(self.root_folder, folders=[n2])
        n2 = Folder.objects.get(pk=n2.pk)
        self.assertEqual(n2.full_name, '/n2')
        n3 = Folder.objects.get(pk=n3.pk)
        self.assertEqual(n3.full_name, '/n2/n3')

        file_3 = File.objects.get(pk=file_3.pk)
        self.assertEqual(file_3.full_name, '/n2/n3/f3')


        n3_1 = Folder.objects.get(pk=n3_1.pk)
        self.assertEqual(n3_1.full_name, '/n2/n3_1')
        n3_2 = Folder.objects.get(pk=n3_2.pk)
        self.assertEqual(n3_2.full_name, '/n2/n3_2')

        file_3_2 = File.objects.get(pk=file_3_2.pk)
        self.assertEqual(file_3_2.full_name, '/n2/n3_2/f3_2')

    def test_replace_nested_folders_restriction(self):
        """Avoid hierarchy collapse"""
        # Create nested folders
        n0 = self.root_folder.addNewFolder('n0') # /n0
        self.assertEqual(n0.full_name, '/n0')
        n1 = n0.addNewFolder('n1') # /n0/n1
        self.assertEqual(n1.full_name, '/n0/n1')
        n0_1 = self.root_folder.addNewFolder('n0_1') # /n0_1
        self.assertEqual(n0_1.full_name, '/n0_1')
        try:
            self.root_folder.replace(n1, folders=[n0, n0_1])
        except Exception as e:
            pass
        
        n0_after_replace = Folder.objects.get(pk=n0.pk)
        self.assertEqual(n0_after_replace.full_name, '/n0')
        n0_1_after_replace = Folder.objects.get(pk=n0_1.pk)
        self.assertEqual(n0_1_after_replace.full_name, '/n0_1')
