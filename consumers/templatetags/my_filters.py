from django import template

register = template.Library()

@register.filter(is_safe=True)
def get_field_value(obj):
    fields = obj._meta.get_fields()
    #print(fields)
    #return "filter tgas"
    res = "<ul>"
    for f in fields:
        fs = f.name.split('.')
        name = fs[-1]
        v = getattr(obj, f.name, name)
        res += f'<li><small>{name}:</small> <strong>{v}</strong></li>'
    res += "</ul>"
    return res