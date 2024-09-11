from core.forms import BaseModelForm
from tracker import models
from django import forms


class TokenForm(BaseModelForm):
    '''
    Form to create a new token
    '''

    token = forms.CharField()

    class Meta:
        model = models.GitToken
        fields = ["service", "label", "token", "is_active"]
