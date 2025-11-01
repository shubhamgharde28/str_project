from django import template
register = template.Library()

@register.filter
def to(value, arg):
    """
    Usage: {% for i in 1|to:12 %}
    Generates a range from value to arg (inclusive)
    """
    return range(value, arg + 1)
