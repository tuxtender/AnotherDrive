from django import forms

class NewFolderNameForm(forms.Form):
    new_name = forms.CharField(max_length=128)

class CommentForm(forms.Form):
    text = forms.CharField(max_length=200)