from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button
from crispy_forms.bootstrap import FormActions


class CrispyHelperMixin:
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
    pass


class BaseModelForm(CrispyHelperMixin, forms.ModelForm):
    pass


class PaginationForm(forms.Form):
    page = forms.CharField(required=False, widget=forms.HiddenInput())
    per_page = forms.CharField(required=False, widget=forms.HiddenInput())
    search = forms.CharField(required=False)
    order_by = forms.ChoiceField(required=False, choices=[])
    order = forms.ChoiceField(
        required=False,
        choices=[
            ("asc", "Ascending"),
            ("desc", "Descending"),
        ],
    )

    def __init__(self, *args, **kwargs):
        order_by_choices = kwargs.pop("order_by_choices", [])
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        if not order_by_choices:
            self.fields.pop("order_by")
            self.fields.pop("order")
        else:
            self.fields["order_by"].choices = order_by_choices
        self.helper.form_method = "GET"
        self.helper.form_id = "paginationFormTest"
        self.helper.field_template = "bootstrap5/layout/inline_field.html"
        self.helper.form_class = "row row-cols-lg-auto g-3 align-items-center"
        self.helper.layout = Layout(
            *self.fields,
            Button("", "Submit", css_class="btn btn-primary"),
        )
