from django.shortcuts import render
from typing import Any
from django.urls import reverse
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


class BaseListView(ListView):
    template_name = "list.html"
    model = None
    title = None
    boolean_fields = []
    list_display = []
    create_url = None
    field_labels = {}
    create_button_label = None
    can_create = True
    can_edit = True
    can_delete = False

    def get_title(self):
        if self.title:
            return self.title
        return self.model._meta.verbose_name_plural.title()

    def get_model_name(self):
        if self.model:
            return self.model._meta.verbose_name.title()
        return self.model._meta.verbose_name.title()

    def get_can_create(self):
        return self.can_create

    def get_can_edit(self):
        return self.can_edit

    def get_can_delete(self):
        return self.can_delete

    def get_create_url(self):
        if self.get_can_create() is False:
            return None
        if self.create_url:
            return self.create_url
        return reverse(
            f"{self.model._meta.app_label}:{self.model._meta.model_name}_create"
        )

    def get_create_button_label(self):
        if self.create_button_label:
            return self.create_button_label
        return f"Create {self.get_model_name()}"

    def get_field_labels(self):
        if not self.list_display:
            raise ValueError("list_display is required")
        return {
            field: self.field_labels.get(
                field, self.model._meta.get_field(field).verbose_name.title()
            )
            for field in self.list_display
        }

    def get_boolean_fields(self):
        if self.boolean_fields:
            return self.boolean_fields
        _boolean_fields = []
        for f in self.list_display:
            field = self.model._meta.get_field(f)
            if field.get_internal_type() == "BooleanField":
                _boolean_fields.append(f)
        return _boolean_fields

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        properties = [
            "title",
            "model_name",
            "can_create",
            "can_edit",
            "can_delete",
            "create_button_label",
            "create_url",
            "boolean_fields",
            "list_display",
            "field_labels",
        ]
        for prop in properties:
            if callable(getattr(self, f"get_{prop}", None)):
                context[prop] = getattr(self, f"get_{prop}")()
            else:
                context[prop] = getattr(self, prop)

        return context
