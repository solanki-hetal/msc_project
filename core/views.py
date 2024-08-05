from django.shortcuts import render
from typing import Any
from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin

# Create your views here.


class FormMixin(SuccessMessageMixin):
    template_name = "form.html"
    title = None
    action = "Save"

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        cleaned_data.update(
            {"model_name": self.model_name(), "action": self.get_action().lower()}
        )
        return super().get_success_message(cleaned_data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"save_label": self.get_action()})
        return kwargs

    def get_title(self):
        if self.title:
            return self.title
        return f"{self.action} {self.model_name()}"

    def get_action(self):
        return self.action

    def model_name(self):
        return self.model._meta.verbose_name.title()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_title()
        context["model_name"] = self.model_name()
        return context


class BaseCreateView(FormMixin, CreateView):
    action = "Create"
    success_message = "%(model_name)s was created successfully."


class BaseUpdateView(FormMixin, UpdateView):
    action = "Update"
    success_message = "%(model_name)s was updated successfully."


# class TokenEditView(UpdateView):
#     form_class = forms.TokenForm
#     template_name = "token_form.html"
#     model = models.GitToken

#     def get_queryset(self):
#         return self.model.objects.filter(user=self.request.user)

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs["instance"] = self.get_object()
#         return kwargs
