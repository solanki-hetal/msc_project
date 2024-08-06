from django import template

register = template.Library()


@register.filter(name="get_value")
def get_value(data, key):
    return data[key]


@register.filter(name="get_property")
def get_property(data, key):
    val = getattr(data, key)
    if val is None:
        return "-"
    return val
