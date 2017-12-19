from django.db import models

# Create your models here.


# 分页demo的表
class Books(models.Model):
    title = models.CharField("书名", max_length=32)
    author = models.CharField("作者", max_length=32)
    country = models.CharField('国家', max_length=32)
    category = models.ForeignKey(verbose_name='分类', to="Category")
    price = models.DecimalField(verbose_name="价格", max_digits=5, decimal_places=2)

    def __str__(self):
        return self.title


class Category(models.Model):
    type_options = (
        (1, "人文社科"),
        (2, "经济管理"),
        (3, "励志与成功"),
        (4, "科技"),
        (5, "文学艺术"),
        (6, "少儿"),
    )
    tp = models.IntegerField("科类", choices=type_options)
    subtypes = models.CharField("子类", max_length=32)

    def __str__(self):
        return self.subtypes
