from django import template

register = template.Library()

@register.filter
def minus(value, arg):
    """Subtracts arg from value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0  # Return 0 if the values are invalid