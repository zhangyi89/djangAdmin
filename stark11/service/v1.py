from django.db.models.base import ModelBase
from django.conf.urls import url
from django.shortcuts import render, HttpResponse




class ModelConfig(object):
    # list_display = ('__str__', )
    # model是models.py中创建的类
    # admin_site是相对应的AdminSite对象
    def __init__(self, model, admin_site):
        self.model = model
        self.admin_site = admin_site

    def __str__(self):
        return "%s.%s" % (self.model._meta.app_label, self.__class__.__name__)

    def get_urls(self):
        # 取出每个model的app_label和model_name用来URL的反向查询
        info = (self.model._meta.app_label, self.model._meta.model_name)
        # 根据每个model生成对应的增删改查等url
        # url格式： /add/
        # /changlist/
        # /(\d+)/change/
        # /(\d+)/delete/

        urlpatterns = [
            # 调用相应的试图函数（self.changelist_view)
            url(r'^$', self.changelist_view, name='%s_%s_changelist' % info),
            url(r'^add/$', self.add_view, name='%s_%s_add' % info),
            url(r'^(\d+)/delete/$', self.delete_view, name='%s_%s_delete' % info),
            url(r'^(\d+)/change/$', self.change_view, name='%s_%s_change' % info)
        ]
        print(urlpatterns)
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls()

    def changelist_view(self, request, *args, **kwargs):
        # 获取表头信息
        head_list= []
        for field_name in self.list_display:
            # 判断传进来的参数是字段名，还是方法
            if isinstance(field_name, str):
                # 根据类和字段的名称，获取字段对象的verbose_name
                verbose_name = self.model._meta.get_field(field_name).verbose_name
            else:
                verbose_name = field_name(self, is_header=True)
            head_list.append(verbose_name)
        # 获取相应model的对象信息
        data_list = self.model.objects.all()
        # 取出每个信息用于在前端显示
        # 由于每个model的字段名称都不一样，所以我们需要把每个model的字段取出来，在传给前端显示
        # new_data_List中保存的是每个一对象的信息
        new_data_list = []
        for obj in data_list:
            # temp中存的是每一个对象的所有字段信息
            temp = []

            for row in self.list_display:
                if isinstance(row, str):
                    # 通过反射，传入的对象为obj，方法名为row（getattr把list_display中的字符串转换成可执行函数名传递给obj这个方法使用)
                    # val是obj.row之后的结果
                    val = getattr(obj, row)
                else:
                    # 传进来的参数如果是一个方法，则直接执行。
                    val = row(self, obj)
                temp.append(val)
            new_data_list.append(temp)
        return render(request, "stark11/changelist.html", {'data_list': new_data_list, "head_list": head_list})

    def add_view(self):
        return HttpResponse("添加页面")

    def delete_view(self):
        return HttpResponse("删除页面")

    def change_view(self):
        return HttpResponse("修改页面")


class AdminSite(object):
    def __init__(self):
        self._registry = {}

    def register(self, model_class, admin_class=None, **kwargs):
        if not admin_class:
            admin_class = ModelConfig
        # model_class可以是一个可迭代对象，如果不是可迭代对象，则转换成列表
        # 用于下面的for循环的条件
        if isinstance(model_class, ModelBase):
            model_class = [model_class]
        for model in model_class:
            # self是一个AdminSite对象
            self._registry[model] = admin_class(model, self)
        # print(self._registry)
        "{ <class 'app01.models.UserInfo'>: <stark11.service.v1.ModelConfig object at 0x105df76a0 >, " \
        "< class 'app01.models.UserType'>: <stark11.service.v1.ModelConfig object at 0x105df7c50 >}"

    # 为每个注册的model_class生成对应的url，并根据ModelAdmin去为对象l生成各自对应的增删改查url
    # 根url格式： app名字/model名字
    def get_urls(self):
        urlpatterns = []
        for model, admin_site in self._registry.items():
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            urlpatterns += [
                # admin_site是一个ModelConfig对象（每个model生成一个ModelConfig对象)
                # admin_site.urls则调用了ModelConfig里面的urls方法，self就是这个对应的model实例化的ModelConfig对象
                url(r'^%s/%s' % (app_label, model_name), (admin_site.urls, None, None))
            ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), None, 'stark11'


site = AdminSite()
