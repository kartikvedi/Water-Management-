from django import template

register = template.Library()


@register.filter(name='item_at_index')
def item_at_index(lst, index):
    try:
        return lst[index]
    except:
        return lst[index]
