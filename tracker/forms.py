from django import forms
from tracker import models

class TokenForm(forms.ModelForm):
    class Meta:
        model = models.GitToken
        fields = ["service", "token"]
        
