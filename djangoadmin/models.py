from django.db import models


# Create your models here.


class User(models.Model):
    name = models.CharField(verbose_name="用户名", max_length=32)
    ut = models.ForeignKey(verbose_name="用户类型", to='UserType')

    class Meta:
        verbose_name_plural = "用户表"

    def __str__(self):
        return self.name


class UserType(models.Model):
    title = models.CharField(verbose_name="类型", max_length=32)
    roles = models.ForeignKey(verbose_name="角色", to='Roles')

    class Meta:
        verbose_name_plural = "用户类型表"

    def __str__(self):
        return self.title


class Roles(models.Model):
    caption = models.CharField(verbose_name="角色", max_length=32)

    class Meta:
        verbose_name_plural = "角色表"

    def __str__(self):
        return self.caption


registry = "{<class 'django.contrib.auth.models.Group'>: <django.contrib.auth.admin.GroupAdmin object at 0x105cb0400>, " \
           "<class 'django.contrib.auth.models.User'>: <django.contrib.auth.admin.UserAdmin object at 0x105ce00f0>, " \
           "<class 'djangoadmin.models.User'>: <djangoadmin.admin.UserAdmin object at 0x105ce9e80>, " \
           "<class 'djangoadmin.models.UserType'>: <djangoadmin.admin.UserTypeAdmin object at 0x105ce9f28>, " \
           "<class 'djangoadmin.models.Roles'>: <djangoadmin.admin.RolesAdmin object at 0x105ce9fd0>} self._registry"