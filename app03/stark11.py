from stark11.service import v1
from app03 import models
from django.conf.urls import url
from django.forms import ModelForm
from django.shortcuts import render, HttpResponse
from django.utils.safestring import mark_safe


# 重写ModelConfig方法
class BooksConfig(v1.ModelConfig):

    # list_display是按照顺序显示的
    list_display = ('id', 'title', 'author', 'country', 'category', 'price')
    filter_display = ('title__contains', 'author__contains','country__contains', 'category__subtypes__contains', )
    action_display = ()
    # comb_filter = ('title', 'author', 'country', 'category')
    comb_filter = [
        # v1.FilterOption('title', ),
        # v1.FilterOption('author', ),
        # v1.FilterOption('country', ),
        v1.FilterOption('category', )
    ]
    # 是否显示添加按钮
    show_add_btn = True

    # 重新赋值model_form_class
    # model_form_class = UserModelForm


v1.site.register(models.Books, BooksConfig)
v1.site.register(models.Category)
