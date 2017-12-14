# from stark import service
from django.utils.safestring import mark_safe

from stark.service import v1
from app01 import models


class UserInfoConfig(v1.StartConfig):

    def checkbox(self, obj):
        return mark_safe("<input type='checkbox' name='pk' value='%s'/>" % (obj.id,))

    def edit(self, obj):
        return mark_safe("<a href='/edit/%s>编辑</a>" % (obj.id, ))

    list_display = [checkbox, 'id', 'name', edit]


v1.site.register(models.UserInfo)

