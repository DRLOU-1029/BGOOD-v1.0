from django import forms

class MyForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    age = forms.IntegerField(label='Age')