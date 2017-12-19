from django.shortcuts import render, redirect, HttpResponse
from django.forms import ModelForm
from app03 import models
# Create your views here.


# 分页demo案例
class BooksModelForm(ModelForm):

    class Meta:
        model = models.Books
        fields = "__all__"


def pagination_demo(request):
    # for i in range(230):
    #     models.Books.objects.create(title="书名%s" % i, author="作者%s" % i, country="美国", category_id=2, price="20")

    book_obj = models.Books.objects.all()
    pager_obj = Pagination(request.GET.get('page', 1), len(book_obj), request.path_info, request.GET)
    book_list = book_obj[pager_obj.start:pager_obj.end]
    html = pager_obj.page_html()
    # get_url = request.GET.urlencode()
    # print(get_url)
    from django.http import QueryDict
    params = QueryDict(mutable=True)
    print(params)
    params['_list_filter'] = request.GET.urlencode()
    print(params)
    get_url = params.urlencode()
    print(get_url)
    return render(request, "pagination-demo.html", {"get_url": get_url, "book_obj": book_obj, 'book_list': book_list, "page_html": html})


class Pagination(object):
    """
    自定义分页
    """
    def __init__(self, current_page, total_count, base_url, params, per_page_count=10, max_pager_count=11):
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1
        if current_page <= 0:
            current_page = 1
        self.current_page = current_page

        # 数据总条数
        self.total_count = total_count

        # 每页显示10条数据
        self.per_page_count = per_page_count

        # 页面上应该显示的最大页码(总大小除以每页的大小）
        max_page_num, div = divmod(total_count, per_page_count)

        # 有余数的情况下
        if div:
            max_page_num += 1
        self.max_page_num = max_page_num

        # 页面上默认显示11个页面（当前页在中间）
        self.max_pager_count = max_pager_count
        # 中间那个的页数
        self.half_max_pager_count = int((max_pager_count - 1) / 2)

        # URL前缀
        self.base_url = base_url

        # request.GET
        import copy
        params = copy.deepcopy(params)
        params._mutable = True

        # 包含当前列表页面所有搜索条件
        self.params = params

    @property
    def start(self):
        return (self.current_page - 1) * self.per_page_count

    @property
    def end(self):
        return self.current_page * self.per_page_count

    def page_html(self):
        # 如果总页数小于每页显示的页数
        if self.max_page_num <= self.max_pager_count:
            pager_start = 1
            pager_end = self.max_page_num
        # 如果总页数大于每页显示的页数
        else:
            # 如果当前页 <= 5
            if self.current_page <= self.half_max_pager_count:
                pager_start = 1
                pager_end = self.max_pager_count
            # 如果当前页 + 5 > 总页码
            else:
                if (self.current_page + self.half_max_pager_count) > self.max_page_num:
                    pager_end = self.max_page_num
                    pager_start = self.max_page_num - self.max_pager_count + 1
                else:
                    pager_start = self.current_page - self.half_max_pager_count
                    pager_end = self.current_page + self.half_max_pager_count
        page_html_list = []
        # 首页
        self.params['page'] = 1
        first_page = '<li><a href="%s?%s" aria-label="Previous"><span aria-hidden="true">首页</span></a></li>' \
                     % (self.base_url, self.params.urlencode(),)
        page_html_list.append(first_page)
        for i in range(pager_start, pager_end + 1):
            if i == self.current_page:
                # temp = '<a class="active" href="%s?page=%s">%s</a>' % (self.base_url,i ,i ,)
                temp = '<li class="active"><a href="%s?page=%s">%s</a></li>' % (self.base_url, i, i,)
            else:
                # temp = '<a href="%s?page=%s">%s</a>' % (self.base_url, i, i,)
                temp = '<li><a href="%s?page=%s">%s</a></li>' % (self.base_url, i, i,)
            page_html_list.append(temp)
        # 尾页
        self.params['page'] = self.max_page_num
        last_page = '<li><a href="%s?%s" aria-label="Previous"><span aria-hidden="true">尾页</span></a></li>' \
                    % (self.base_url, self.params.urlencode(),)
        page_html_list.append(last_page)
        return ''.join(page_html_list)


def edit(request, nid):
    if request.method == "GET":
        print(request.GET)
        obj = models.Books.objects.filter(pk=nid)[0]
        form = BooksModelForm(instance=obj)
        return render(request, "edit.html", {"form": form})
    else:
        print(request.GET)
        print(request.GET.urlencode())
        url = "/pagination-demo/?%s" % (request.GET.urlencode())
        # return HttpResponse("ok")

        return redirect(url)
