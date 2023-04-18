from django import forms
from django.forms import Form


class SolutionEditForm(Form):
    solution = forms.CharField(widget=forms.Textarea(attrs={'rows': 20}))
