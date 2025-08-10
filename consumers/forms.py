from django import forms

class upload_defectives_form(forms.Form):
  file = forms.FileField()
  
class update_consumer_master_form(forms.Form):
  file = forms.FileField()
  