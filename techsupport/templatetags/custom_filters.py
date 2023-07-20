from django import template

register = template.Library()

@register.filter
def cycle_color(value):
    colors = ['primary', 'secondary', 'success', 'danger', 'warning', 'info']
    return colors[value % len(colors)]
