from django.template import Library

register = Library()


@register.inclusion_tag('list.html')
def changelist(request):

    data = "111"
    return {"data": data}
