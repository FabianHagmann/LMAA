from django import forms
from django.forms import Form


class SolutionEditForm(Form):
    """
    Single field form for viewing and updating a solution
    """
    solution = forms.CharField(widget=forms.Textarea(attrs={'rows': 20}))
