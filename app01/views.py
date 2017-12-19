from django.shortcuts import render

# Create your views here.
from utils.pager import Pagination
from app03 import models

HOST_LIST = []
for i in range(1, 349):
    HOST_LIST.append("x%s.com" % i)


def hosts(request):
    pager_obj = Pagination(request.GET.get('page', 1), len(HOST_LIST), request.path_info)
    host_list = HOST_LIST[pager_obj.start:pager_obj.end]
    html = pager_obj.page_html()
    return render(request, 'hosts.html', {'host_list': host_list, 'page_html': html})


USER_LIST = []
for i in range(1,231):
    USER_LIST.append("user%s" % i)


def users(request):
    pager_obj = Pagination(request.GET.get('page', 1), len(USER_LIST), request.path_info)
    user_list = USER_LIST[pager_obj.start:pager_obj.end]
    html = pager_obj.page_html()
    return render(request, 'users.html', {'user_list': user_list, "page_html": html})

