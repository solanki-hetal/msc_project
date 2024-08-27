from typing import Any

from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView

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


class ListAction:
    def __init__(self, label, icon, action, class_name=None, tooltip=None):
        self.label = label
        self.icon = icon
        self.action = action
        self.class_name = class_name
        self.tooltip = tooltip


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
    actions = []
    paginate_by = 25
    per_page_options = [10, 25, 50, 100]

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

    def get_paginate_by(self, queryset) -> int | None:
        return self.request.GET.get("per_page", self.paginate_by)

    def to_query_string(self, **kwargs):
        query_string = self.request.GET.copy()
        for key, value in kwargs.items():
            query_string[key] = value
        return query_string.urlencode()

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            return super().get(request, *args, **kwargs)
        except Http404 as e:
            queryset = self.get_queryset()
            paginator = self.get_paginator(queryset, self.get_paginate_by(queryset))
            if int(request.GET.get("page", 1)) > paginator.num_pages:
                return redirect(
                    request.path + "?" + self.to_query_string(page=paginator.num_pages)
                )
            raise e

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
            "actions",
            "per_page_options",
        ]
        for prop in properties:
            if callable(getattr(self, f"get_{prop}", None)):
                context[prop] = getattr(self, f"get_{prop}")()
            else:
                context[prop] = getattr(self, prop)
        paginator = context["paginator"]
        total_pages = paginator.num_pages
        current_page = int(self.request.GET.get("page", 1))
        print(current_page, total_pages)
        if current_page > total_pages:
            # Redirect to the last page if the current page exceeds the total number of pages
            context["page_obj"] = paginator.page(total_pages)
        return context
