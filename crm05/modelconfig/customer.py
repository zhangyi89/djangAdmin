import json
import datetime

import os
from django.conf.urls import url
from django.db import transaction
from django.db.models import Q
from django.forms import ModelForm
from django.http import QueryDict, FileResponse
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from stark11.service import v1
from utils import message
from crm05 import models


class SingleModelForm(ModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant', 'status', 'recv_date', 'last_consult_date']


class CustomerConfig(v1.ModelConfig):

    def get_course(self, obj=None, is_header=False):
        if is_header:
            return "咨询课程"
        course_list = obj.course.all()
        html = []
        for item in course_list:
            temp = "<a style='display:inline-block;padding:1px 3px;border:1px solid gray;margin-right:2px;' " \
                   "href='/stark11/crm05/customer/%s/%s/dc/'>%s X</a>" \
                   % (obj.pk, item.pk, item.name)
            html.append(temp)
        return mark_safe("".join(html))

    def get_gender(self, obj=None, is_header=False):
        if is_header:
            return "性别"
        return obj.get_gender_display()

    def get_education(self, obj=None, is_header=False):
        if is_header:
            return "学历"
        return obj.get_education_display()

    def get_work_status(self, obj=None, is_header=False):
        if is_header:
            return "工作状态"
        return obj.get_work_status_display()

    def get_status(self, obj=None, is_header=False):
        if is_header:
            return "状态"
        return obj.get_status_display()

    def get_source(self, obj=None, is_header=False):
        if is_header:
            return "来源"
        return obj.get_source_display()

    def record(self, obj=None, is_header=False):
        if is_header:
            return "跟进记录"
        return mark_safe('<a href="/stark11/crm05/consultrecord/?customer=%s">查看跟进记录</a>' % (obj.pk, ))

    list_display = ('name', 'qq', get_gender, get_education, get_work_status,
                    get_course, get_status, get_source, 'consultant', record,
                    'date', 'recv_date')

    filter_display = ('name__contains', 'course__name__contains', )

    order_by_display = ('-status',)

    def delete_course_view(self, request, customer_id, course_id):
        """
        删除当前课程
        :param request: request信息
        :param customer_id: 用户id
        :param course_id:  课程id
        :return:
        """
        customer_obj = self.model.objects.filter(pk=customer_id).first()
        customer_obj.course.remove(course_id)
        # 跳转回去的时候，要保留原来的搜索条件
        # 保留之前的搜索条件，并生成URL地址
        # query_str = self.request.GET.urlencode()  # page=2&nid=1
        # params = QueryDict(mutable=True)
        # params[self.config._query_param_key] = query_str
        # return mark_safe('<a href="%s?%s">%s</a>' % (self.config.get_change_url(pk), params.urlencode(), text,))
        query_str = self.request.GET.urlencode()
        params = QueryDict(mutable=True)
        params[self._query_param_key] = query_str

        return redirect(self.get_changelist_url() + "? %s " % params.urlencode())

    def extra_url(self):
        """
        自定义增加的url信息
        :return:
        """
        app_model_name = (self.model._meta.app_label, self.model._meta.model_name,)
        patterns = [
            url(r'^(\d+)/(\d+)/dc/$', self.wrapper(self.delete_course_view), name="%s_%s_dc" % app_model_name),
            url(r'^public/$', self.wrapper(self.public_view), name="%s_%s_public" % app_model_name),
            url(r'^(\d+)/competition/$', self.wrapper(self.competition_view), name="%s_%s_competition" % app_model_name),
            url(r'^user/$', self.wrapper(self.user_view), name="%s_%s_user" % app_model_name),
            url(r'^single/$', self.wrapper(self.single_view), name="%s_%s_single" % app_model_name),
            url(r'^multi/$', self.wrapper(self.multi_view), name="%s_%s_multi" % app_model_name),
            url(r'^file_down/$', self.wrapper(self.file_down), name="%s_%s_file_down" % app_model_name),
            url(r'^report/$', self.wrapper(self.report), name="%s_%s_file_down" % app_model_name)
        ]
        return patterns

    def public_view(self, request):
        """
        公共客户资源
        :return:
        """
        # 条件：未报名 并且（15天未成单（当前时间-15）> 接客时间） or 3天未跟进（当前时间-3天 > 最后跟进时间）） Q对象
        #  当前时间
        now_time = datetime.datetime.now().date()
        deadline_time = now_time - datetime.timedelta(days=15)
        follow_time = now_time - datetime.timedelta(days=3)
        # Q 方法1
        # customer_list = models.Customer.objects.filter(Q(recv_date__lt=deadline_time) | Q(last_consult_date__lt=follow_time), status=2)

        # Q 方法二
        con = Q()
        q1 = Q()
        q1.connector = 'OR'
        q1.children.append(('recv_date__lt', deadline_time))
        q1.children.append(('last_consult_date__lt', follow_time))
        q2 = Q()
        q2.connector = 'OR'
        q2.children.append(('status', 2))
        con.add(q1, "AND")
        con.add(q2, "AND")
        customer_list = models.Customer.objects.filter(con)
        return render(request, "public_view.html", {'customer_list': customer_list})

    def competition_view(self, request, cid):
        """
        抢单
        :param request:
        :return:
        """
        current_user_id = 1
        # 抢单时需要修改的数据： recv_date 、last_consult_date 、 consultant
        ctime = datetime.datetime.now().date()
        # 可以抢单的要求： 1、必须原顾问不是自己 2、状态必须是未报名 3、3/15天的两个条件限制
        # models.Customer.objects.filter(id=cid).
        # update(recv_date=ctime,last_consult_date=ctime,consultant_id=current_user_id)
        ctime = datetime.datetime.now().date()
        no_deal = ctime - datetime.timedelta(days=15)  # 接客
        no_follow = ctime - datetime.timedelta(days=3)  # 最后跟进日期
        row_count = models.Customer.objects.filter(Q(recv_date__lt=no_deal) | Q(last_consult_date__lt=no_follow), status=2, id=cid)\
            .exclude(consultant_id=current_user_id).update(recv_date=ctime, last_consult_date=ctime, consultant_id=current_user_id)
        if not row_count:
            return HttpResponse("手慢无")
        models.CustomerDistribution.objects.create(user_id=current_user_id, customer_id=cid, ctime=ctime)
        return HttpResponse("抢单成功")

    def user_view(self, request):
        """
        当前登录用户的所有客户
        :param request:
        :return:
        """
        # 在session中获取当前用户的ID
        current_user_id = 1

        # 当前用户的所有客户列表
        customers = models.CustomerDistribution.objects.filter(user_id=current_user_id).order_by('status')
        return render(request, "user_view.html", {'customers': customers})

    def single_view(self, request):
        """
        单条录入客户信息
        :param request:
        :return:
        """
        if request.method == "GET":
            # 录入的信息表需要排除一些字段，在SingleModelForm中有体现
            form = SingleModelForm()
            return render(request, "single_view.html", {'form': form})
        else:
            # 提交录入数据
            from crm05.salerole import Salerole
            form = SingleModelForm(request.POST)
            if form.is_valid():
                sale_id = Salerole.get_sale_id()
                if not sale_id:
                    return HttpResponse("无销售顾问，无法进行分配")
                # try:
                with transaction.atomic():
                    # data = form.cleaned_data
                    # data['consultant_id'] = int(sale_id)
                    # course_list = request.POST.getlist("course")
                    # data.pop('course')
                    ctime = datetime.datetime.now().date()
                    # customer_obj = models.Customer.objects.create(**data)
                    # customer_obj.course.add(*[models.Course.objects.get(id=i) for i in course_list])
                    form.instance.consultant_id = sale_id
                    form.instance.recv_date = ctime
                    form.instance.last_consult_date = ctime
                    # 创建客户表
                    customer_obj = form.save()
                    """客户表新增数据：
                        - 获取该分配的课程顾问id
                        - 当前时间
                    客户分配表中新增数|}
                        - 获取新创建的客户ID
                        - 顾问ID
                    """
                    # 客户分配表
                    models.CustomerDistribution.objects.create(user_id=sale_id, customer=customer_obj, ctime=ctime)

                    # 发送消息
                    message.send_message('2369717781@qq.com', '名字', '主题', '内容')

                # except Exception as e:
                #     # 创建客户表和客户分配表异常
                #     # 回滚从iter中取出的id到失误表里
                #     Salerole.rollback(sale_id)
                #     return HttpResponse("录入异常")
                return HttpResponse('录入成功')

            else:
                return render(request, 'single_view.html', {'form': form})

    def multi_view(self, request):
        if request.method == "GET":
            return render(request, "multi_view.html")
        else:
            # 获取文件句柄
            from django.core.files.uploadedfile import InMemoryUploadedFile
            file_obj = request.FILES.get("exfile")
            # 保存文件到本地
            with open("uploadfile.xlsx", mode="wb") as f:
                for chunk in file_obj:
                    f.write(chunk)
            # 读出数据
            import xlrd
            # 打开文件
            workbook = xlrd.open_workbook("uploadfile.xlsx")
            # 获取文件中表格名称列表
            # sheet_names = workbook.sheet_names()
            # 取第一个表格对象
            # sheet = workbook.sheet_by_name(sheet_names[0])
            sheet = workbook.sheet_by_index(0)
            # 定义表格模版结构
            maps = {
                0: "name",
                1: "gender",
                2: "qq",
                3: "status"
            }
            # 一共有多少数据行（排除了标题行）
            for index in range(1, sheet.nrows):
                # 每一行的数据 [text:'lucy', number:18.0, text:'女']  <class 'list'>
                row = sheet.row(index)
                row_dict = {}
                for i in range(len(maps)):
                    key = maps[i]
                    cell = row[i]
                    print(cell, type(cell))  # text:'lucy' <class 'xlrd.sheet.Cell'>
                    row_dict[key] = cell.value  # {'name': 'Jack', 'gender': '男', 'QQ': 11112222002.0, 'status': '已报名'}
                if row_dict["gender"] == "男":
                    row_dict["gender"] = 1
                else:
                    row_dict["gender"] = 2
                if row_dict["status"] == "已报名":
                    row_dict["status"] = 1
                else:
                    row_dict["status"] = 2
                # 自动获取ID
                # 录入客户表
                # 录入客户分配表
                # consultant_id
                ctime = datetime.datetime.now().date()
                from crm05.salerole import Salerole
                sale_id = Salerole.get_sale_id()
                row_dict['consultant_id'] = sale_id
                row_dict['recv_date'] = ctime
                row_dict["last_consult_date"] = ctime
                with transaction.atomic():
                    # 客户表
                    customer_obj = models.Customer.objects.create(**row_dict)
                    # 客户分配表
                    models.CustomerDistribution.objects.create(user_id=sale_id, customer=customer_obj, ctime=ctime)
            return HttpResponse("ok")
    """
    def multi_view(self, request):
        if request.method == "GET":
            return render(request, "multi_view.html")
        else:
            # 获取文件句柄
            from django.core.files.uploadedfile import InMemoryUploadedFile
            file_obj = request.FILES.get("exfile")
            # 保存文件到本地
            with open("uploadfile.xlsx", mode="wb") as f:
                for chunk in file_obj:
                    f.write(chunk)
            # 读出数据
            import xlrd
            # 打开文件
            workbook = xlrd.open_workbook("uploadfile.xlsx")
            # 获取文件中表格名称列表
            # sheet_names = workbook.sheet_names()
            # 取第一个表格对象
            # sheet = workbook.sheet_by_name(sheet_names[0])
            sheet = workbook.sheet_by_index(0)
            # 定义表格模版结构
            maps = {
                0: "name",
                1: "gender",
                2: "qq",
                3: "status"
            }
            # 一共有多少数据行（排除了标题行）
            for index in range(1, sheet.nrows):
                # 每一行的数据 [text:'lucy', number:18.0, text:'女']  <class 'list'>
                row = sheet.row(index)
                row_dict = {}
                for i in range(len(maps)):
                    key = maps[i]
                    cell = row[i]
                    print(cell, type(cell))  # text:'lucy' <class 'xlrd.sheet.Cell'>
                    row_dict[key] = cell.value  # {'name': 'Jack', 'gender': '男', 'QQ': 11112222002.0, 'status': '已报名'}
                if row_dict["gender"] == "男":
                    row_dict["gender"] = 1
                else:
                    row_dict["gender"] = 2
                if row_dict["status"] == "已报名":
                    row_dict["status"] = 1
                else:
                    row_dict["status"] = 2
                # 自动获取ID
                # 录入客户表
                # 录入客户分配表
                # consultant_id
                ctime = datetime.datetime.now().date()
                from crm05.salerole import Salerole
                sale_id = Salerole.get_sale_id()
                row_dict['consultant_id'] = sale_id
                row_dict['recv_date'] = ctime
                row_dict["last_consult_date"] = ctime
                with transaction.atomic():
                    # 客户表
                    customer_obj = models.Customer.objects.create(**row_dict)
                    # 客户分配表
                    models.CustomerDistribution.objects.create(user_id=sale_id, customer=customer_obj, ctime=ctime)
            return HttpResponse("ok")
    """

    def file_down(self, request):
        file = open("/Users/zhangyi/Desktop/my-project/CRM/static/stark11/multifile.xlsx", "wb")
        print(file)
        # # 循环读取文件
        # while True:
        #     chunk = file.read(262144)
        #     if chunk:
        #         yield chunk
        #     else:
        #         break
        # file.close()
        # 创建文件对象
        response = FileResponse(file)
        # ﻿设定文件头，这种设定可以让任意文件都能正确下载
        response['Content-Type'] = 'application/octet-stream'
        # ﻿设定传输给客户端的文件名称
        response['Content-Disposition'] = 'attachment; filename="example.tar.gz'
        # 传给客户端的文件大小
        # response['Content-Length'] = os.path.getsize(file)
        return response

    def report(self, request):
        # ﻿公司级别，查看2017每个月成单量
        from django.db.models import Count
        v11 = models.CustomerDistribution.objects.filter(ctime__year=2017, status=2).extra(select={'mt': 'strftime("%%Y-%%m", ctime)'}).values('mt', 'user__username').annotate(ct=Count('id'))
        # select strftime("%Y-%m", ctime) as ftime, count('id') as ct  from tb where status=2 and strftime("%Y", ctime)=2017 group by ftime
        # 每个月的已成单的
        # {name: '小刘', data: [5, 3, 4, 7, 2]}
        print(v11)  # <QuerySet [{'mt': '2017-12', 'ct': 3}]>
        # <QuerySet [{'mt': '2017-12', 'user__username': 'jack', 'ct': 1}, {'mt': '2017-12', 'user__username': 'lucy', 'ct': 2}]>

        v1 = models.CustomerDistribution.objects.filter(ctime__year=2017, status=2).extra(select={'mt': 'strftime("%%Y-%%m", ctime)'}).values('mt').annotate(ct=Count('id'))
        # 每个月的客户量
        v2 = models.CustomerDistribution.objects.filter(ctime__year=2017).extra(select={'mt': 'strftime("%%Y-%%m", ctime)'}).values('mt').annotate(ct=Count('id'))
        # 某个时间段的销售记录
        start_date= "2017-1-1"
        end_date = '2017-12-31'
        all_list = models.CustomerDistribution.objects.filter(ctime__gte=start_date, ctime__lte=end_date, status=2).values('user_id', 'ctime')
        return render(request, "reportform/report3.html")
