from django.conf.urls import url
from django.shortcuts import render, HttpResponse

from stark.service import v1
from app01 import models


class StartConfig(object):
    list_display = []

    def __init__(self, model_class, site):
        self.model_class = model_class
        self.site = site

    def get_urls(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        urlpatterns = [
            url('r^$', self.changelist_view, name='%s_%s_changelist' % app_model_name),
            url('r^add/$', self.add_view, name='%s_%s_add' % app_model_name),
            url(r'^(\d+)/delete/$', self.delete_view, name='%s_%s_delete' % app_model_name),
            url(r'^(\d+)/change/$', self.change_view, name='%s_%s_change' % app_model_name),
        ]

    @property
    def urls(self):
        return self.get_urls()

    def changelist_view(self, request, *args, **kwargs):
        data_list = self.model_class.objects.all()
        new_data_list = []

        for row in data_list:
            temp = []
            for field_name in self.list_display:
                if isinstance(field_name, str):
                    val = getattr(row, field_name)
                else:
                    val = field_name(self, row)
                temp.append(val)
            new_data_list.append(temp)
        return render(request, 'stark/list.html', {"data_list": new_data_list})

    def add_view(self, request, *args, **kwargs):
        return HttpResponse("添加")

    def delete_view(self, request, *args, **kwargs):
        return HttpResponse("删除")

    def change_view(self, request, *args, **kwargs):
        return HttpResponse("修改")


class StarkSite(object):
    def __init__(self):
        self._registry = {}

    def register(self, model_class, stark_config_class=None):
        if not stark_config_class:
            stark_config_class = StartConfig
        self._registry[model_class] = stark_config_class(model_class, self)

    def get_urls(self):
        urlpatterns = []
        for model, stark_config_obj in self._registry.items():
            print(self._registry.items())
            app_label = model._meta.app_label
            model_name = model._meta.model_name

            urlpatterns += [
                url(r'^%s/%s' %(app_label, model_name), (stark_config_obj.urls, None, None))
            ]

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), None, 'stark'


site = StarkSite()
