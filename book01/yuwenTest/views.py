from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader, RequestContext
from yuwenTest.models import BookInfo  # 导入图书模型类


# Create your views here.
# 1. 定义视图函数
# 2. 进行url配置 建立url和视图的对应的关系  miniweb    flask 框架使用装饰器来实现


# http://127.0.0.1:8000/index
def my_render(request, template_path, context_dict={}):  # 定义一个默认值
    '''使用模板文件 '''
    # 加载模板文件
    temp = loader.get_template(template_path)  # 一个模板对象
    # 定义模板上下文（给模板文件传递数据）
    context = RequestContext(request, context_dict)  # 不传入数据的时候 传入一个空字典
    # 模板渲染（得到一个标准的html内容）
    res_html = temp.render(context)
    # 返回给浏览器
    return HttpResponse(res_html)


def index(request):  # request是一个HttpRequest对象
    # 进行处理 和 M和T进行交互
    # 最后需要返回一个 HttpResponse对象

    # return HttpResponse('老铁没毛病')
    #
    # 进行url配置  建立请求和地址的联系

    # 使用模板文件
    '''
        1. 加载模板文件（去模板目录下获得 html 文件的内容 得到一个模板对象）
        2. 定义模板上下文（给模板文件传递数据）
        3. 模板渲染（得到一个标准的html内容）
    '''
    # return my_render(request, 'yuwenTest/index.html')
    # 调用django自己写的render方法 原理与我们自己写的my_render方法一样
    return render(request, 'yuwenTest/index.html', {"content": "hello world", "list": list(range(1, 10))})


def index2(request):
    # 127.0.0.1:8000/index2
    return HttpResponse('人生苦短，我用python')


def show_books(request):
    '''显示图书的信息'''
    # 1.通过M查找图书表中的数据
    books = BookInfo.objects.all()
    # 2.使用模板
    return render(request, 'yuwenTest/show_books.html', {'books': books})


def detail(request, bid):
    '''查询图书关联的信息'''
    # 1.根据bid查询图书信息
    book = BookInfo.objects.get(id=bid)
    # 2.查询和book关联的英雄信息
    heros = book.heroinfo_set.all()
    # 3.使用模板
    return render(request, 'yuwenTest/detail.html', {'book': book, 'heros': heros})
    
def detail(request,nid):
    return HttpResponse(nid)
