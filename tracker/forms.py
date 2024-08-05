from core.forms import BaseModelForm
from tracker import models
from django import forms


class TokenForm(BaseModelForm):

    token = forms.CharField()

    class Meta:
        model = models.GitToken
        fields = ["service", "token"]
