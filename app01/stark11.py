from django.conf.urls import url
from django.forms import ModelForm
from django.shortcuts import render, HttpResponse
from django.utils.safestring import mark_safe

from stark11.service import v1
from app01 import models


# 通过v.site实例化对象，register方法注册model类
# 传参：第一个参数为model类。第二个参数为定制ModleConfig，如果不传，则会调用默认的ModeConfig类
# 通过ModelConfig可以定制也前端页面的显示内容与方式


# 重写UserInfo的ModelForm方法
class UserModelForm(ModelForm):
    class Meta:
        model = models.UserInfo
        fields = '__all__'
        error_messages = {
            'name': {
                'required': '用户不能为空'
            }
        }


# 重写ModelConfig方法
class UserInfoConfig(v1.ModelConfig):

    # def checkbox(self, obj=None, is_header=False):
    #     if is_header:
    #         return "选择"
    #     return mark_safe('<input type="checkbox" name="pk" value="%s">' % (obj.id, ))
    #
    # def edit(self, obj=None, is_header=False):
    #     if is_header:
    #         return "编辑"
    #     return mark_safe('<a href="/edit/%s">编辑</a>' % (obj.id,))

    def func(self):
        return HttpResponse("测试扩展自定义URL")

    # 扩展自定义URL
    def extra_url(self):
        url_list = [
            url(r'stark11/test/$', self.func),
        ]
        return url_list

    # list_display是按照顺序显示的
    list_display = ('id', 'name',)

    # 是否显示添加按钮
    show_add_btn = True

    # 重新赋值model_form_class
    model_form_class = UserModelForm


v1.site.register(models.UserInfo, UserInfoConfig)
v1.site.register(models.UserType)
