from collections.abc import Sequence
from typing import Any

from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView
from django.db.models import Q

from core.forms import PaginationForm

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
    filter_form_class = PaginationForm
    order_by_choices = None
    searchable_fields = []

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
        per_page = self.request.GET.get("per_page")
        if not per_page:
            return self.paginate_by
        return int(per_page)

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

    def get_filter_form_kwargs(self):
        kwargs = {}
        if self.order_by_choices is not None:
            kwargs["order_by_choices"] = self.order_by_choices
        kwargs['has_search'] = bool(self.searchable_fields)
        return kwargs

    def get_filter_form(self):
        return self.filter_form_class(self.request.GET, **self.get_filter_form_kwargs())

    def get_ordering(self) -> Sequence[str]:
        order_by = self.request.GET.get("order_by")
        order = self.request.GET.get("order", "asc")
        if order_by:
            return [f"{'' if order == 'asc' else '-'}{order_by}"]
        return super().get_ordering()

    def get_searchable_query(self):
        search = self.request.GET.get("search")
        if not self.searchable_fields or not search:
            return Q()
        if isinstance(self.searchable_fields, str):
            return Q(**{f"{self.searchable_fields}__icontains": search})
        filters = {}
        query = Q()
        if isinstance(self.searchable_fields, dict):
            for field, lookup in self.searchable_fields.items():
                filters[f"{field}__{lookup}"] = search
        elif isinstance(self.searchable_fields, Sequence):
            for field in self.searchable_fields:
                filters[f"{field}__icontains"] = search
        for key, value in filters.items():
            query |= Q(**{key: value})
        return query

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(self.get_searchable_query())

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
        paginator = self.get_paginator(self.object_list, self.get_paginate_by(self.object_list))
        total_pages = paginator.num_pages
        current_page = self.request.GET.get("page", 1)
        if not current_page:
            current_page = 1
        current_page = int(current_page)
        if current_page > total_pages:
            # Redirect to the last page if the current page exceeds the total number of pages
            context["page_obj"] = paginator.page(total_pages)
        page_range = []
        start = max(1, current_page - 1)
        end = min(total_pages, current_page + 1)
        if start > 1:
            page_range.append(1)
            if start > 2:
                page_range.append("...")
        for i in range(start, end + 1):
            page_range.append(i)
        if end < total_pages:
            if end < total_pages - 1:
                page_range.append("...")
            page_range.append(total_pages)
        context["page_range"] = page_range
        context["filter_form"] = self.get_filter_form()
        return context
