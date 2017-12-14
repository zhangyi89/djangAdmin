from django.db import models

# Create your models here.


class UserInfo(models.Model):
    name = models.CharField(verbose_name="用户名", max_length=32)

    def __str__(self):
        return self.name


class UserType(models.Model):
    caption = models.CharField(verbose_name="用户类型", max_length=32)

    def __str__(self):
        return self.caption

