from django import forms

class upload_defectives_form(forms.Form):
  file = forms.FileField()
  