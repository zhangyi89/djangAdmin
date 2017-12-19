from django.db.models import Q
from django.db.models.base import ModelBase
from django.conf.urls import url
from django.forms import ModelForm
from django.http import QueryDict
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe


class ChangeList(object):
    def __init__(self, config, queryset):
        self.config = config

        self.list_display = config.get_list_display()
        self.model = config.model
        self.request = config.request
        self.show_add_btn = config.get_show_add_btn()
        self.show_filter_btn = config.get_show_filter_btn()
        self.show_action_btn = config.get_show_action_btn()
        self.query_param_key = '_list_filter'
        self.filter_btn_val = config.request.GET.get(config._query_param_key, '')

        from utils.pager import Pagination
        # 获取当前页面，默认为1
        current_page = self.request.GET.get('page', 1)
        # 获取总数
        total_count = queryset.count()
        # 实例化Pagination对象
        page_obj = Pagination(current_page, total_count, self.request.path_info, self.request.GET,
                              per_page_count=10, max_pager_count=11)
        self.page_obj = page_obj

        # 根据分页功能，截取data_list的开始和结束
        self.data_list = queryset[page_obj.start:page_obj.end]

    def head_list(self):
        """
        构造表头
        :return:
        """
        result = []
        for field_name in self.list_display:
            if isinstance(field_name, str):
                # 根据类和字段名获取verbose_name
                verbose_name = self.model._meta.get_field(field_name).verbose_name
            else:
                verbose_name = field_name(self.config, is_header=True)
            result.append(verbose_name)
        return result

    def body_list(self):
        """
        处理表中的数据
        :return:
        """
        data_list = self.data_list
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
                    val = row(self.config, obj)
                temp.append(val)
            new_data_list.append(temp)
        return new_data_list


class ModelConfig(object):
    # list_display = ('__str__', )
    list_display = []
    filter_display = []
    action_display = []

    # model是models.py中创建的类
    # admin_site是相对应的AdminSite对象

    def __init__(self, model, admin_site):
        self.model = model
        self.admin_site = admin_site
        self.request = None
        self._query_param_key = '_list_filter'

    def __str__(self):
        return "%s.%s" % (self.model._meta.app_label, self.__class__.__name__)

    # 扩展url，用户重写之后，获取到的url列表会extend到urlpatterns里面
    def extra_url(self):
        return []

    # 过滤搜索条件
    def get_filter_configuration(self):
        key_word = self.request.GET.get(self._query_param_key)
        filter_fields = self.get_filter_display()
        condition = Q()
        condition.connector = 'or'
        if key_word and self.get_show_filter_btn():
            for fields_name in filter_fields:
                condition.children.append((fields_name, key_word))
        return condition

    # 装饰URL地址，为了是request参数传给每个视图函数
    def wrapper(self, view_func):
        def inner(request, *args, **kwargs):
            self.request = request
            return view_func(request, *args, **kwargs)

        return inner

    # 动态获取每个model的增删改查url
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
            url(r'^$', self.wrapper(self.changelist_view), name='%s_%s_changelist' % info),
            url(r'^add/$', self.wrapper(self.add_view), name='%s_%s_add' % info),
            url(r'^(\d+)/delete/$', self.wrapper(self.delete_view), name='%s_%s_delete' % info),
            url(r'^(\d+)/change/$', self.wrapper(self.change_view), name='%s_%s_change' % info)
        ]
        urlpatterns.extend(self.extra_url())
        return urlpatterns

    show_add_btn = True

    # 是否显示添加按钮
    def get_show_add_btn(self):
        return self.show_add_btn

    show_filter_btn = True

    # 是否显示过滤按钮
    def get_show_filter_btn(self):
        return self.show_filter_btn

    show_action_btn = True

    # 是否显示批量操作按钮
    def get_show_action_btn(self):
        return self.show_action_btn

    # 反向获取url
    def get_changelist_url(self):
        name = "stark11:%s_%s_changelist" % (self.model._meta.app_label, self.model._meta.model_name)
        # 反向生成url
        changelist_url = reverse(name)
        return changelist_url

    def get_change_url(self, nid):
        name = "stark11:%s_%s_change" % (self.model._meta.app_label, self.model._meta.model_name)
        # 反向生成url
        change_url = reverse(name, args=(nid,))
        return change_url

    def get_add_url(self):
        name = "stark11:%s_%s_add" % (self.model._meta.app_label, self.model._meta.model_name)
        # 反向生成url
        add_url = reverse(name)
        return add_url

    def get_delete_url(self, nid):
        name = "stark11:%s_%s_delete" % (self.model._meta.app_label, self.model._meta.model_name)
        # 反向生成url
        delete_url = reverse(name, args=(nid,))
        return delete_url

    # 自定义显示字段
    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return "选择"
        return mark_safe('<input type="checkbox" name="pk" value="%s">' % (obj.id,))

    def edit(self, obj=None, is_header=False):
        if is_header:
            return "编辑"
        # 获取GET搜索的信息
        query_str = self.request.GET.urlencode()  # 把数据打包成 page=2&nid=1
        # 如果搜索条件的情况下
        if query_str:
            # 重新构造搜索的数据结构
            # 实例化一个QueryDict对象， QueryDict对象的urlencode方法具有把get后面的信息变成字符串的形式，并且可以一个key对应多个value
            params = QueryDict(mutable=True)
            # 定义一个QueryDict的k v值，把打包的数据复制给新的QueryDict对象的k，
            params[self._query_param_key] = query_str
            # print(params)  # <QueryDict: {'_list_filter': ['page=22']}>
            # print(params.urlencode())  # 在把这个新的QueryDict数据打包 _list_filter=page%3D22
            return mark_safe('<a class="btn btn-info" href="%s?%s">编辑</a>' % (self.get_change_url(obj.id), params.urlencode(),))

        return mark_safe('<a class="btn btn-info" href="%s">编辑</a>' % self.get_change_url(obj.id))

    def delete(self, obj=None, is_header=False):
        if is_header:
            return "删除"
        return mark_safe('<a class="btn btn-danger" href="%s">删除</a>' % self.get_delete_url(obj.id))

    # 获取显示字段列表
    def get_list_display(self):
        data = []
        if self.list_display:
            data.extend(self.list_display)
            data.append(ModelConfig.edit)
            data.append(ModelConfig.delete)
            data.insert(0, ModelConfig.checkbox)
        return data

    # 获取过滤字段列表
    def get_filter_display(self):
        data = []
        if self.filter_display:
            data.extend(self.filter_display)
        return data

    # 获取力量操作方法列表
    def get_action_display(self):
        data = []
        if self.action_display:
            data.extend(self.action_display)
        return data

    # 调用get_urls()方法
    @property
    def urls(self):
        return self.get_urls()

    model_form_class = None

    # 获取ModelForm函数为视图函数使用
    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class

        # 创建ModelForm方法一
        """
        class AdminModelForm(ModelForm):
            class Meta:
                model = self.model
                fields = "__all__"
        """
        # 创建ModelForm方法二
        meta = type('Meta', (object,), {'model': self.model, "fields": "__all__"})
        AdminModelForm = type('AdminModelForm', (ModelForm,), {'Meta': meta})
        return AdminModelForm

    # 增删改查视图函数
    def changelist_view(self, request, *args, **kwargs):
        """
        # 把方法改造到ChangList类里面
        # 获取表头信息
        head_list = []
        for field_name in self.get_list_display():
            # 判断传进来的参数是字段名，还是方法
            if isinstance(field_name, str):
                # 根据类和字段的名称，获取字段对象的verbose_name
                verbose_name = self.model._meta.get_field(field_name).verbose_name
            else:
                verbose_name = field_name(self, is_header=True)
            head_list.append(verbose_name)
        """

        # 通过get_filter_configuration()获取到的条件获取出需要显示的数据列表
        queryset = self.model.objects.filter(self.get_filter_configuration())
        # 通过ChangeList对数据进行处理，self参数是传给了config
        cl = ChangeList(self, queryset)

        """
        # 导入Pagination,为了生成分页功能
        from utils.pager import Pagination
        # 获取当前页面，默认为1
        current_page = request.GET.get('page', 1)
        # 获取总数
        total_count = self.model.objects.all().count()
        # 获取当前URl
        base_url = request.path_info
        # 当前搜索参数
        params = request.GET
        # 实例化Pagination对象
        page_obj = Pagination(current_page, total_count, base_url, params, per_page_count=10, max_pager_count=11)

        # 获取相应model的对象信息
        data_list = self.model.objects.all()
        # 根据分页功能，截取data_list的开始和结束
        data_list = data_list[page_obj.start:page_obj.end]
       
        # 取出每个信息用于在前端显示
        # 由于每个model的字段名称都不一样，所以我们需要把每个model的字段取出来，在传给前端显示
        # new_data_List中保存的是每个一对象的信息

        new_data_list = []
        for obj in data_list:
            # temp中存的是每一个对象的所有字段信息
            temp = []

            for row in self.get_list_display():
                if isinstance(row, str):
                    # 通过反射，传入的对象为obj，方法名为row（getattr把list_display中的字符串转换成可执行函数名传递给obj这个方法使用)
                    # val是obj.row之后的结果
                    val = getattr(obj, row)
                else:
                    # 传进来的参数如果是一个方法，则直接执行。
                    val = row(self, obj)
                temp.append(val)
            new_data_list.append(temp)
            self.get_show_add_btn()
             """
        # return render(request, "stark11/changelist.html", {'data_list': new_data_list, "head_list": head_list,
        #                                                    "show_add_btn": self.get_show_add_btn(),
        #                                                    "add_url": self.get_add_url(), 'page_obj': page_obj})
        return render(request, "stark11/changelist.html", {"cl": cl})

    def add_view(self, request, *args, **kwargs):
        model_form_class = self.get_model_form_class()
        if request.method == "GET":
            form = model_form_class()
            return render(request, "stark11/add_view.html", {"form": form})
        else:
            form = model_form_class(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_changelist_url())
            return render(request, "stark11/add_view.html", {"form": form})

    def delete_view(self, request, nid, *args, **kwargs):
        self.model.objects.filter(pk=nid).delete()
        return redirect(self.get_changelist_url())

    def change_view(self, request, nid, *args, **kwargs):
        model_from_class = self.get_model_form_class()
        obj = self.model.objects.filter(pk=nid).first()

        if request.method == "GET":
            form = model_from_class(instance=obj)
            return render(request, "stark11/change_view.html", {"form": form})
        if request.method == "POST":
            form = model_from_class(instance=obj, data=request.POST)
            if form.is_valid():
                form.save()
                # 获取搜索的条件信息,get方法对自动urlencode
                list_query_str = request.GET.get(self._query_param_key)  # page=22
                # 获取列表页面并且携带有从GET里面获取的过滤条件
                list_url = "%s?%s" % (self.get_changelist_url(), list_query_str)
                return redirect(list_url)
            else:
                return redirect(self.get_changelist_url())


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
                url(r'^%s/%s/' % (app_label, model_name), (admin_site.urls, None, None))
            ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), None, 'stark11'


site = AdminSite()
