"""CRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from stark.service import v1
from stark11.service import v1
from app01 import views as view1
from app03 import views as view2

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^stark/', v1.site.urls),
    # 通过v1.site是实例化一个对象，并调用urls方法
    url(r'^stark11/', v1.site.urls),

    # 分页练习
    url(r'^hosts/$', view1.hosts),
    url(r'^users/$', view1.users),


    # 分页demo
    url(r'^pagination-demo/$', view2.pagination_demo),

    url(r'^app03/edit/(\d+)$', view2.edit)
]
