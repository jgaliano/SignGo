from django import template

register = template.Library()

@register.filter
def replace_comma(value):
    try:
        valor_float = float(str(value).replace(",", "."))
        return "{:,.2f}".format(valor_float)
    except (ValueError, TypeError):
        return value