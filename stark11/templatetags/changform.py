from django.template import Library
from django.forms.models import ModelChoiceField
from django.urls import reverse

from stark11.service.v1 import site
register = Library()


@register.inclusion_tag('stark11/form.html')
def form(config, model_form_obj):
    form_list = []
    for bfield in model_form_obj:
        data = {}
        # print(bfield.field)  # <django.forms.fields.CharField object at 0x10d703390>
        # 通过isinstance判断是否属于Fk或则M2M字段
        from django.forms.boundfield import BoundField
        from django.db.models.query import QuerySet
        from django.forms.models import ModelChoiceField
        if isinstance(bfield.field, ModelChoiceField):
            # 获取到类名
            related_class_name = bfield.field.queryset.model
            # 判断类名是否已经注册
            if related_class_name in site._registry:
                data["field"] = bfield
                data['popup'] = True

                # Fk,one, M2M:当前字段所在的类名，和related_name
                model_name = config.model._meta.model_name
                related_name = config.model._meta.get_field(bfield.name).rel.related_name

                # 通过反向解析获取URl
                popup_url = reverse(
                    'stark11:%s_%s_add' % (related_class_name._meta.app_label, related_class_name._meta.model_name))
                popurl = "%s?_popbackid=%s&model_name=%s&related_name=%s" % (popup_url, bfield.auto_id, model_name, related_name)
                data['popup_url'] = popurl
                form_list.append(data)
        else:
            data["field"] = bfield
            form_list.append(data)
    return {'form': form_list}

