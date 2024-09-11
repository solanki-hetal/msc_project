from collections.abc import Sequence
from typing import Any

from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView
from django.db.models import Q

from core.forms import PaginationForm




class FormMixin(SuccessMessageMixin):
    '''
    Mixin for form views that displays a form and a title.
    It also sets the success message to be displayed after the form is submitted successfully.
    action: str - The action label to be shown on the form. Default is "Save".
    template_name: str - The template to be used to render the form. Default is "form.html".
    title: str - The title to be displayed on the form. Default is None.
    '''
    template_name = "form.html"
    title = None
    action = "Save"

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        '''
        Creates a success message to be displayed after the form is submitted successfully.
        cleaned_data: dict - The cleaned data from the form.
        Returns a string.
        default: "%(model_name)s was %(action)s successfully."
        '''
        cleaned_data.update(
            {"model_name": self.model_name(), "action": self.get_action().lower()}
        )
        return super().get_success_message(cleaned_data)

    def get_form_kwargs(self):
        '''
        Adds the save_label argument to the form constructor.
        '''
        kwargs = super().get_form_kwargs()
        kwargs.update({"save_label": self.get_action()})
        return kwargs

    def get_title(self):
        '''
        Returns the title to be displayed on the form.
        If title is not set, it returns "{action} {model_name}".
        '''
        if self.title:
            return self.title
        return f"{self.action} {self.model_name()}"

    def get_action(self):
        return self.action

    def model_name(self):
        '''
        Returns the model name in title case. eg. ModelName -> Model Name
        '''
        return self.model._meta.verbose_name.title()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        '''
        Adds the title and model_name to the context.
        This will be available in the template.
        '''
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_title()
        context["model_name"] = self.model_name()
        return context


class BaseCreateView(FormMixin, CreateView):
    '''
    Create View for creating new objects.
    '''
    action = "Create"
    success_message = "%(model_name)s was created successfully."


class BaseUpdateView(FormMixin, UpdateView):
    '''
    Update View for updating existing objects.
    '''
    action = "Update"
    success_message = "%(model_name)s was updated successfully."


class ListAction:
    '''
    class for list actions.
    
    '''
    def __init__(self, label, icon, action, class_name=None, tooltip=None):
        '''
        label: str - The label to be displayed on the action button.
        icon: str - The icon to be displayed on the action button.
        action: str - The action to be performed when the button is clicked.
        class_name: str - The css classes to be added to the action button. Default is None.
        tooltip: str - The tooltip to be displayed when the mouse hovers over the action button. Default is None.
        '''
        self.label = label
        self.icon = icon
        self.action = action
        self.class_name = class_name
        self.tooltip = tooltip


class BaseListView(ListView):
    '''
    List View for displaying a list of objects.
    template_name: str - The template to be used to render the list. Default is "list.html".
    model: Model - The model to be used for the list. Default is None.
    title: str - The title to be displayed on the list. Default is None.
    boolean_fields: list - The list of boolean fields to be displayed as checkboxes. Default is [].
    This is used while rendering the list, for boolean fields it will show "Cross" or "Check" based on true/false.
    list_display: list - The list of fields to be displayed in the list. This is a required field.
    create_url: str - The URL to redirect to when the create button is clicked. Default is None.
    field_labels: dict - The labels to be displayed for the fields in the list. Default is {}.
    					 if not provided, it will use the verbose name of the field.
						if provided, it will use the provided label for specified field.
    create_button_label: str - The label to be displayed on the create button. Default is None.
    can_create: bool - Whether the create button should be displayed or not. Default is True.
    can_edit: bool - Whether the edit button should be displayed or not. Default is True.
    can_delete: bool - Whether the delete button should be displayed or not. Default is False.
    actions: list - The list of actions to be displayed on the list. Default is [].
    paginate_by: int - The number of objects to be displayed per page. Default is 25.
    per_page_options: list - The list of options to be displayed in the per page dropdown. Default is [10, 25, 50, 100].
    filter_form_class: Form - The form class to be used for filtering the list. Default is PaginationForm.
    order_by_choices: list - The list of choices to be displayed in the order by dropdown. Default is None.
    searchable_fields: list - The list of fields to be searched when "search" param is present in GET request. Default is [].
							- If not provided, it will not search any field.
							- You can provide a list of fields to be searched.
							- You can provide a dictionary of field:lookup to be searched.
							- You can provide a string to search all fields using icontains lookup.	
    '''
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
        '''
        Generate field labels for the list display fields.
        if field_labels is provided, it will use the provided label for specified field.
        if not provided, it will use the verbose name of the field.
        '''
        if not self.list_display:
            raise ValueError("list_display is required")
        return {
            field: self.field_labels.get(
                field, self.model._meta.get_field(field).verbose_name.title()
            )
            for field in self.list_display
        }

    def get_boolean_fields(self):
        '''
        if boolean_fields is provided, it will use the provided boolean fields.
        if not provided, it will loop through the fields present in model and Identify BooleanFields and mark them.
        '''
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
        '''
        Get the filter form kwargs.
        '''
        kwargs = {}
        if self.order_by_choices is not None:
            kwargs["order_by_choices"] = self.order_by_choices
        kwargs['has_search'] = bool(self.searchable_fields)
        return kwargs

    def get_filter_form(self):
        return self.filter_form_class(self.request.GET, **self.get_filter_form_kwargs())

    def get_ordering(self) -> Sequence[str]:
        '''
        Decide how to order the queryset.
        If order_by is present in GET request, order by that field.
        else order by the default ordering.
        '''
        order_by = self.request.GET.get("order_by")
        order = self.request.GET.get("order", "asc")
        if order_by:
            return [f"{'' if order == 'asc' else '-'}{order_by}"]
        return super().get_ordering()

    def get_searchable_query(self):
        '''
        Get the query to search the searchable fields.
        '''
        search = self.request.GET.get("search")
        # if searchable_fields is not provided, return empty query
        if not self.searchable_fields or not search:
            return Q()
        # if searchable_fields is a string, search all fields using icontains lookup
        if isinstance(self.searchable_fields, str):
            return Q(**{f"{self.searchable_fields}__icontains": search})
        filters = {}
        query = Q()
        # if searchable_fields is a dictionary, search the fields using the provided lookup
        # eg. {"field1": "icontains", "field2": "exact"} -> Q(field1__icontains=search)| Q(field2__exact=search)
        if isinstance(self.searchable_fields, dict):
            for field, lookup in self.searchable_fields.items():
                filters[f"{field}__{lookup}"] = search
		# if searchable_fields is a list, search all fields using icontains lookup
        elif isinstance(self.searchable_fields, Sequence):
            for field in self.searchable_fields:
                filters[f"{field}__icontains"] = search
        # create the query
        for key, value in filters.items():
            query |= Q(**{key: value})
        return query

    def get_queryset(self):
        queryset = super().get_queryset()
        # search the queryset based on the search query
        return queryset.filter(self.get_searchable_query())

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # properties to be added to the context
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
            # for each property, check if there is a method to get the value
            # if there is a method, call the method to get the value
            # eg. get_title, get_model_name, get_can_create, etc
            # if the method is not present, it will get the value from the object
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
        # Page range to be displayed in the pagination
        # get the current page and the pages before and after the current page
        # eg. if current page is 5, it will display 4, 5, 6
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
