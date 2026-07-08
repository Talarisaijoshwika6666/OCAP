from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Dict lookup by a *variable* key inside a template — Django's
    built-in `dict.key` syntax only supports literal keys, so MCQ answers
    (keyed by mcq_id, an int) need this filter instead."""
    if not dictionary:
        return None
    return dictionary.get(key)
