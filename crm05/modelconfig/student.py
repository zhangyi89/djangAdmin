import json
from django.conf.urls import url
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from stark11.service import v1
from crm05 import models


class StudentConfig(v1.ModelConfig):

    def extra_url(self):
        app_model_name = (self.model._meta.app_label, self.model._meta.model_name)
        urlpatterns = [
            url(r'^(\d+)/sv/$', self.wrapper(self.scores_view), name="%s_%s_sv" % app_model_name),
            url(r'^chart/$', self.wrapper(self.scores_chart), name="%s_%s_chart" % app_model_name),
        ]
        return urlpatterns

    def scores_view(self, request, sid):
        # 查看当前学生
        obj = models.Student.objects.filter(id=sid).first()
        if not obj:
            return HttpResponse("查无此人")
        # 获取当前学生所有的班级
        class_list = obj.class_list.all()
        return render(request, "scores_view.html", {'class_list': class_list, "sid": sid})

    def scores_chart(self, request):
        # 根据hchart所需要的条件构建数据结构
        ret = {'status': False, 'data': None, 'message': None}
        try:
            cid = request.GET.get('cid')
            sid = request.GET.get('sid')
            record_list = models.StudyRecord.objects.filter(student_id=sid, course_record__class_obj_id=cid,).order_by('course_record_id')
            data = []
            for row in record_list:
                day = "day%s" % row.course_record.day_num
                data.append([day, row.score])
            ret['data'] = data
            ret['status'] = True
        except Exception as e:
            ret['message'] = '获取失败'
        return HttpResponse(json.dumps(ret))

    def display_scores(self, obj=None, is_header=False):
        if is_header:
            return "查看成绩"

        surls = reverse("stark11:crm05_student_sv", args=(obj.pk, ))
        return mark_safe("<a href='%s'>点击查看</a>" % surls)

    list_display = ('username', display_scores)


