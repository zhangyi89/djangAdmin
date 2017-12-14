from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class Stark11Config(AppConfig):
    name = 'stark11'

    # 添加启动程序时自动查找的模块
    def ready(self):
        autodiscover_modules('stark11')