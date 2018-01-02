from django.conf.urls import url
from django.forms import Form, fields, widgets
from django.http import QueryDict, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe

from stark11.service import v1
from crm05.modelconfig.student import StudentConfig
from crm05.modelconfig.customer import CustomerConfig
from . import models


class UserInfoConfig(v1.ModelConfig):
    list_display = ('name', 'username', 'depart')
    filter_display = ('name__contains', 'username__contains', 'depart__id__contains')
    comb_filter = [
        # v1.FilterOption('name'),
        # v1.FilterOption('username'),
        # 这里的x是self.data的data,data是option.get_queryset(_field)对象
        v1.FilterOption('depart', text_func_name=lambda x: str(x), val_func_name=lambda x: x.code)
    ]


v1.site.register(models.UserInfo, UserInfoConfig)


v1.site.register(models.Student, StudentConfig)


class ClassListConfig(v1.ModelConfig):

    def course_semester(self, obj=None, is_header=False):
        if is_header:
            return "班级"
        return "%s(%s期)" % (obj.course.name, obj.semester,)

    def course_teacher(self, obj=None, is_header=False):
        if is_header:
            return "老师"
        teacher_list = obj.teachers.all()
        html = []
        for item in teacher_list:
            html.append(item.name)
        return ', '.join(html)

    def course_num(self, obj=None, is_header=False):
        if is_header:
            return "班级人数"
        # 查看该班级的学生数据
            # obj是班级对象
            # 学生和班级的关系 M2M
        num = obj.student_set.count()
        return num

    list_display = ('school', course_semester, course_num, 'price', 'start_date', 'memo', course_teacher, 'tutor')

    comb_filter = [
        v1.FilterOption("school",),
        v1.FilterOption("course", multi=True)
    ]


v1.site.register(models.ClassList, ClassListConfig)


class ConsultRecordConfig(v1.ModelConfig):
    list_display = ('customer', 'consultant', 'date')
    filter_display = ('customer__name__contains', )
    comb_filter = [
        v1.FilterOption('customer')
    ]

    def changelist_view(self, request, *args, **kwargs,):
        """
        重写changelist_view为了判断该用户的权限，是否显示record列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        customer = request.GET.get("customer")
        # session获取当前用户ID
        current_login_user_id = request.session.get("user_id")
        ct = models.Customer.objects.filter(consultant=current_login_user_id, id=customer).count()
        if not ct:
            return HttpResponse("别抢客户！！！")
        return super(ConsultRecordConfig, self).changelist_view(request, *args, **kwargs)


v1.site.register(models.ConsultRecord, ConsultRecordConfig)


class CourseConfig(v1.ModelConfig):
    list_display = ('name',)


v1.site.register(models.Course, CourseConfig)


class CourseRecordConfig(v1.ModelConfig):

    def extra_url(self):
        app_model_name = (self.model._meta.app_label, self.model._meta.model_name)
        urlpatterns = [
            url(r'^(\d+)/score_list/$', self.wrapper(self.score_list), name="%s_%s_score_list" % app_model_name)
        ]
        return urlpatterns

    def score_list(self, request, record_id):
        """
        学生成绩信息
        :param request:
        :param score_id: 老师上课记录id
        :return:
        """
        # get请求返回页面
        if request.method == "GET":
            data = []
            # 获取这个record的所有学生对象
            study_record_list = models.StudyRecord.objects.filter(course_record_id=record_id)
            for obj in study_record_list:
                # obj是对象
                tempForm = type('tempForm', (Form, ), {
                    "score_%s" % obj.pk: fields.ChoiceField(choices=models.StudyRecord.score_choices),
                    "homework_note_%s" % obj.pk: fields.CharField(widget=widgets.Textarea())
                })
                data.append({'obj': obj, 'form': tempForm(
                    initial={'score_%s' % obj.pk: obj.score, 'homework_note_%s' % obj.pk: obj.homework_note})})
            return render(request, 'score_list.html', {'data': data})
        else:
            data_dict = {}
            for key, value in request.POST.items():
                if key == "csrfmiddlewaretoken":
                    continue
                name, nid = key.rsplit("_", 1)
                if nid in data_dict:
                    data_dict[nid][name] = value
                else:
                    data_dict[nid] = {name: value}
                for nid, update_dict in data_dict.items():
                    models.StudyRecord.objects.filter(id=nid).update(**update_dict)
            return redirect(request.path_info)

    def attendance(self, obj=None, is_header=False):
        if is_header:
            return "考勤"
        return mark_safe("<a href='/stark11/crm05/studyrecord/?course_record=%s'>考勤管理</a> " % obj.pk)

    def display_score_list(self, obj=None, is_header=False):
        if is_header:
            return "成绩录入"
        rurl = reverse("stark11:crm05_courserecord_score_list", args=(obj.pk, ))
        return mark_safe("<a href='%s'>成绩录入</a> " % rurl)

    list_display = ('class_obj', 'day_num', 'teacher', attendance, display_score_list)


v1.site.register(models.CourseRecord, CourseRecordConfig)


v1.site.register(models.Customer, CustomerConfig)


class DepartConfig(v1.ModelConfig):
    list_display = ('title', 'code')
    filter_display = ('title', )
    # comb_filter = [
    #     v1.FilterOption('title')
    # ]
    edit_display = ('title',)


v1.site.register(models.Department, DepartConfig)
v1.site.register(models.PaymentRecord)
v1.site.register(models.School)


class StudyRecordConfig(v1.ModelConfig):

    def display_record(self, obj=None, is_header=False):
        if is_header:
            return "出勤"
        return obj.get_record_display()

    list_display = ('course_record', 'student', display_record)
    # filter_display = ('student__name__contains', )

    show_comb_filter = False
    comb_filter = [
        v1.FilterOption("course_record"),
        v1.FilterOption("student")
    ]

    def action_checked(self, request):
        pk_list = request.POST.getlist("pk")
        models.StudyRecord.objects.filter(id__in=pk_list).update(record="checked")
    action_checked.short_desc = "签到"

    def action_vacate(self, request):
        pk_list = request.POST.getlist("pk")
        models.StudyRecord.objects.filter(id__in=pk_list).update(record="vacate")
    action_vacate.short_desc = "请假"

    def action_late(self, request):
        pk_list = request.POST.getlist("pk")
        models.StudyRecord.objects.filter(id__in=pk_list).update(record="late")
    action_late.short_desc = "迟到"

    def action_noshow(self, request):
        pk_list = request.POST.getlist("pk")
        models.StudyRecord.objects.filter(id__in=pk_list).update(record="noshow")
    action_noshow.short_desc = "缺勤"

    def action_leave_early(self, request):
        pk_list = request.POST.getlist("pk")
        models.StudyRecord.objects.filter(id__in=pk_list).update(record="leave_early")
    action_leave_early.short_desc = "早退"

    action_display = [action_checked, action_vacate, action_late, action_noshow, action_leave_early]


v1.site.register(models.StudyRecord, StudyRecordConfig)


class SaleRankConfig(v1.ModelConfig):
    list_display = ('user', 'num', 'weigth')


v1.site.register(models.SaleRank, SaleRankConfig)