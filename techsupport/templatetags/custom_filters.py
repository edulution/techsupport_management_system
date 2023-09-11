from django import template

register = template.Library()

@register.filter
def cycle_color(value):
    colors = ['primary', 'secondary', 'success', 'danger', 'warning', 'info']
    return colors[value % len(colors)]

@register.filter
def add_placeholder(field, placeholder_text):
    field.field.widget.attrs.update({'placeholder': placeholder_text})
    return field

@register.filter
def add_class(field, class_name):
    if 'class' in field.field.widget.attrs:
        field.field.widget.attrs['class'] += f' {class_name}'
    else:
        field.field.widget.attrs['class'] = class_name
    return field