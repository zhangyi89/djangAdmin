from django.utils.safestring import mark_safe

from stark11.service import v1
from app01 import models


# 通过v.site实例化对象，register方法注册model类
# 传参：第一个参数为model类。第二个参数为定制ModleConfig，如果不传，则会调用默认的ModeConfig类
# 通过ModelConfig可以定制也前端页面的显示内容与方式

# 重写ModelConfig方法
class UserInfoConfig(v1.ModelConfig):

    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return "选择"
        return mark_safe('<input type="checkbox" name="pk" value="%s">' % (obj.id, ))

    def edit(self, obj=None, is_header=False):
        if is_header:
            return "编辑"
        return mark_safe('<a href="/edit/%s">编辑</a>' % (obj.id,))

    # list_display是按照顺序显示的
    list_display = (checkbox, 'id', 'name', edit)


v1.site.register(models.UserInfo, UserInfoConfig)
v1.site.register(models.UserType)
