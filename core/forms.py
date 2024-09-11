from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button
from crispy_forms.bootstrap import FormActions


class CrispyHelperMixin:
    """
    * A helper class to add crispy forms to the form
    * This class is a mixin class that can be used to add crispy forms to a form
    * It adds a save and cancel button to the form
    * The save button has a default label of "Save" but can be changed by passing a save_label argument
      to the class constructor
    """

    def __init__(self, *args, **kwargs) -> None:
        save_label = kwargs.pop("save_label", "Save")
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            *self.fields,
            FormActions(
                Submit("save", save_label),
                Button("cancel", "Cancel"),
            ),
        )


class BaseForm(CrispyHelperMixin, forms.Form):
    """
    A base form class that adds crispy forms to the form
    This class can be used to create forms
    """

    pass


class BaseModelForm(CrispyHelperMixin, forms.ModelForm):
    """
    A model form class that adds crispy forms to the form
    This class can be used to create forms for specific models
    """

    pass


class PaginationForm(forms.Form):
    """
    * Form for pagination to be used across the list views
    * This form is used to paginate the list views
    * It has fields for page, per_page, search, order_by and order
    * The page and per_page fields are hidden fields
    * The search field is optional and can be hidden by passing has_search=False to the class constructor
    * The order_by field is a choice field and the choices can be passed to the class constructor using the order_by_choices argument
    * The order field is a choice field with choices of "asc" and "desc"
    * The form uses the GET method
    """

    page = forms.CharField(required=False, widget=forms.HiddenInput())
    per_page = forms.CharField(required=False, widget=forms.HiddenInput())
    search = forms.CharField(required=False)
    order_by = forms.ChoiceField(required=False, choices=[])
    order = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Select Order"),
            ("asc", "Ascending"),
            ("desc", "Descending"),
        ],
    )

    def __init__(self, *args, **kwargs):
        order_by_choices = kwargs.pop("order_by_choices", [])
        has_search = kwargs.pop("has_search", False)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        if not order_by_choices:
            self.fields.pop("order_by")
            self.fields.pop("order")
        else:
            self.fields["order_by"].choices = [
                ("", "Order By"),
                *order_by_choices,
            ]
        if not has_search:
            self.fields.pop("search")

        self.helper.form_method = "GET"
        self.helper.form_id = "paginationFormTest"
        self.helper.field_template = "bootstrap5/layout/inline_field.html"
        self.helper.form_class = "row row-cols-lg-auto g-3 align-items-center"
        if ["page", "per_page"] != list(self.fields.keys()):
            self.helper.layout = Layout(
                *self.fields,
                Button("", "Submit", css_class="btn btn-primary"),
            )
