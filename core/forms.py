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
            )
        )


class BaseForm(CrispyHelperMixin, forms.Form):
    pass


class BaseModelForm(CrispyHelperMixin, forms.ModelForm):
    pass
