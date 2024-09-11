from django import template

register = template.Library()



# Get value from a dictionary
@register.filter(name="get_value")
def get_value(data, key):
    return data[key]


# Get property from an object
@register.filter(name="get_property")
def get_property(data, key):
    val = getattr(data, key)
    if val is None:
        return "-"
    return val



# get a specifit type of URL for an object
# eg, Delete, Update, Detail, etc
@register.filter(name="get_action_url")
def get_action_url(obj, action):
    return obj.get_action_url(action)
