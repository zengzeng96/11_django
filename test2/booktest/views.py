from django.shortcuts import render,redirect # 导入重定向函数
from booktest.models import BookInfo,HeroInfo,AreaInfo
from datetime import date
from django.http import HttpResponse,HttpResponseRedirect

# Create your views here.
def index(request):
    '''显示图书信息'''
    # 1.查询出所有的图书的信息
    books=BookInfo.objects.all()
    # 2.使用模板
    return render(request, 'booktest/index.html',{'books':books})

def create(request):
    '''新增一本图书'''
    # 1.创建一个BookInfo对象
    b=BookInfo()
    b.btitle='神雕侠侣'
    b.bpub_date=date(1985,4,1)
    # 2.保存进数据库
    b.save()
    # 3.返回应答  让浏览器再访问 /index 需要导入一个类
    # return HttpResponse('ok')
    # return HttpResponseRedirect('/index')#重定向
    #上面的这个是复杂的写法
    return redirect('/index')

def delete(request,bid):
    '''删除点击的图书'''
    # 1.通过bid获取要删除的图书对象
    book=BookInfo.objects.get(id=bid)
    # 2.删除
    book.delete()
    # 3.重定向到  /index
    # return HttpResponseRedirect('/index')#重定向
    return redirect('/index')#重定向

def areas(request):
    '''获取广州市的上级地区和下级地区'''
    # 1.获取广州市的信息
    area=AreaInfo.objects.get(atitle='巴中市')
    # 2.查询广州市的上级地区  多对1
    parent=area.aParent
    # 3.查询广州市的下级地区  一对多
    children=area.areainfo_set.all()
    # 4.使用模板
    return render(request, 'booktest/areas.html',{'area':area,'parent':parent,'children':children})


