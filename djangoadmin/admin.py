from django.contrib import admin
from django.forms import widgets
from django.utils.html import format_html
from djangoadmin import models

# Register your models here.
"""
# 传统注册admin
admin.site.register(models.Roles)
admin.site.register(models.UserType)
admin.site.register(models.User)
"""

# 定制admin的注册
# 方式一
# admin.site.register(models.User, UserAdmin)  # 第一个参数可以是个列表

"""
#方式二
@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'ut')
"""

#
# class MyTextArea(widgets.Widget):
#     def __init__(self, attrs=None):
#         # Use slightly better defaults than HTML's 20x2 box
#         default_attrs = {'cols': '40', 'rows': '10'}
#         if attrs:
#             default_attrs.update(attrs)
#         super(MyTextArea, self).__init__(default_attrs)
#
#     def render(self, name, value, attrs=None):
#         if value is None:
#             value = ''
#         final_attrs = self.build_attrs(attrs, name=name)
#         return format_html('<textarea {}>\r\n{}</textarea>', final_attrs, value)



# 定制admin
@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'ut', )  # 显示
    list_display_links = ('name', )  # 链接
    list_filter = ("name",)          # 右侧过滤
    list_select_related = False      # 查表是否关联
    list_per_page = 100              # 每页显示条数
    list_max_show_all = 200          # 显示全部（小于200条时）
    list_editable = ("ut",)          # 可编辑状态
    search_fields = ("name",)        # 可通过该字段搜索
    preserve_filters = True          # 跳转回列表后，是否返回到过滤状态
    save_on_top = False
    save_as = False
    raw_id_fields = ("ut",)         # 把FK  M2M变成input框的形式
    fields = ("name",)
    # formfield_overrides = {            # 详细页面显示指定插件
    #     models.models.CharField: {'widget': MyTextArea},
    # }


@admin.register(models.UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'roles', )


@admin.register(models.Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ("caption",)


