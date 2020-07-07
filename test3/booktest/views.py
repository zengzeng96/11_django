from datetime import datetime, timedelta

from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from booktest.models import AreaInfo, PicTest

# Create your views here.
EXCLUDE_IPS=['192.168.0.114']
#闭包函数
def block_ips(view_func):
    def wrapper(request,*args,**kwargs):
        user_ip=request.META['REMOTE_ADDR']
        if user_ip in EXCLUDE_IPS:
            return HttpResponse("<h1>Forbidden</h1>")
        else:
            return view_func(request,*args,**kwargs)
    return wrapper
# request就是 HttpRequest类型的对象
# 包含浏览器请求的信息
# 既可以通过装饰器来实现  但是这么多视图函数前面都要价格装饰器比较麻烦
# 也可以通过中间件 middleware.py  来实现  它是在视图函数执行之前执行的
# @block_ips
def index01(request):
    print('<'*30,'__index__01','>'*30)
    return render(request, 'booktest/index01.html')
    
def index(request):
    # print(request.method)
    print(request.path)#表示请求的页面的完整路径  不包含域名和参数部分
    # print(request.encoding)#如果为None值 则表示浏览器的默认设置 一般为utf-8

    # print(request.method)
    # num='a'+1#导致错误视图
    # 获取浏览器端的ip地址
    # user_ip=request.META['REMOTE_ADDR']
    # if user_ip in EXCLUDE_IPS:
    #     return HttpResponse("<h1>Forbidden</h1>")
    # print('user_ip:', user_ip)
    print('__index__')

    return render(request, 'booktest/index.html')

# @block_ips
def show_arg1(request,bid):#捕获参数  位置参数
    return HttpResponse(bid)

# @block_ips
def show_arg(request,num):#捕获参数  关键字参数  num必须与正则匹配的组名一样
    return HttpResponse(num)

# @block_ips
def login(request):
    '''显示登陆页面'''
    # 判断用户是否登陆
    if request.session.has_key('islogin'):
        #说明用户已经登陆 直接跳转到首页
        return redirect('/index')
    else:
        # 说明用户未登陆
        # 获取cookie username
        if 'username' in request.COOKIES:
            # 获取记住的用户名
            username=request.COOKIES['username']
        else:
            username=''

        return render(request, 'booktest/login.html',{'username':username})

# @block_ips
def login_check(request):
    print(request.method)
    '''登陆校验视图'''
    # 1.获取提交的用户名和密码
    # print(type(request.POST))
    # django.http.request.QueryDict
    # from django.http.request import QueryDict
    # q=QueryDict('a=1&b=2&c=3')
    # q['a']的值就是1    等价于  q.get('a')
    # q['b']的值就是2
    # q['c']的值就是3
    # 他与字典最大的不同就是他可以一个键对应多个值 例如：
    # q=QueryDict('a=1&a=2&a=3&b=4')
    # q.get('a')==q['a']------>'3'   #只是获取最后一个
    # q.getlist('a')--------->['1','2','3'] #获取所有的
    username=request.POST.get('username')
    password=request.POST.get('password')
    remember=request.POST.get('remember')
    print('username:', username)
    print('password:', password)
    print('remember:',remember)
    # 2.进行校验
    # 实际开发 根据用户名和密码查找数据库
    # 模拟 假设正确用户名： smart   正确密码：123
    if username=='smart' and password=='123':
        #用户名密码正确   跳转到首页
        response=redirect('/index')#他的返回值就是一个httpResponseRedirect对象
        if remember=='on':
            # 设置cookie  username  过期时间为一周
            response.set_cookie('username',username,max_age=7*24*3600)
        #记住用户的登陆状态
        #只要session中有islogin  就认为用户已经登陆
        request.session['islogin']=True
        return response
    else:
        #用户名或密码错误  跳转到登陆页面
        return redirect('/login')

    # 3.返回应答
    # return render(request, template_name)
    # return HttpResponse('ok')
    # request对象的属性
# /test_ajax
# @block_ips
def ajax_test(request):
    '''显示ajax页面'''
    return render(request, 'booktest/test_ajax.html')

# @block_ips
def ajax_handle(request):
    '''ajax处理'''
    # 假设返回的json数据{'res':1}
    return JsonResponse({'res':1})


# /login_ajax
# @block_ips
def login_ajax(request):
    '''显示ajax登陆页面'''
    return render(request, 'booktest/login_ajax.html')

# /login_ajax_check
# @block_ips
def login_ajax_check(request):
    '''显示ajax校验页面'''
    # 1.获取提交的用户名和密码
    username=request.POST.get('username')
    password=request.POST.get('password')
    # 2.进行校验，返回json数据
    if username=='smart' and password=='123':
        #用户名和密码正确
        return JsonResponse({'res':1})#ajax请求在后台 不要返回页面或者重定向 通过回调函数来跳转

    else:
        #用户名和密码错误
        return JsonResponse({'res':0})



# /set_cookie
# @block_ips
def set_cookie(request):
    '''设置cookie信息'''
    response=HttpResponse('设置cookie')
    #设置一个cookie信息  名字为num  值为 1
    response.set_cookie('num1',1,max_age=14*24*3600)
    # response.set_cookie('num2',1,expires=datetime.now()+timedelta(days=14))
    #max_age 设置cookie的过期时间   时间为s
    #expire   设置cookie的过期时间  上面设置的是14天之后过期
    return response

# /get_cookie
# @block_ips
def get_cookie(request):
    '''获取cookie的信息'''
    # 取出cookie   num的值
    num=request.COOKIES['num1']
    return HttpResponse(num)

# /set_session
# @block_ips
def set_session(request):
    '''设置session'''
    request.session['username']='smart'
    request.session['age']=18
    request.session.set_expiry(5)#sessionid 十秒钟之后过期
    return HttpResponse({'设置session'})

# /get_session
# @block_ips
def get_session(request):
    '''获取session'''
    username=request.session['username']
    age=request.session['age']
    return HttpResponse(username+':'+str(age))

# @block_ips
def clear_session(request):
    '''清除session信息'''
    # request.session.clear()
    request.session.flush()
    return HttpResponse('删除ok')


# /static_test
# @block_ips
def static_test(request):
    '''静态文件'''
    print(settings.STATICFILES_FINDERS)
    # ('django.contrib.staticfiles.finders.FileSystemFinder', 'django.contrib.staticfiles.finders.AppDirectoriesFinder')
    # 先在配置的文件夹下找
    # 再在app的文件夹下找
    return render(request, 'booktest/static_test.html')


# /show_upload
def show_upload(request):
    '''显示上传图片页面'''
    return render(request, 'booktest/upload_pic.html')


# /upload_handle
def upload_handle(request):
    '''上传图片处理'''
    # 1.获取上传文件的处理对象
    pic = request.FILES["pic"]
    # pic=request.FILES["pic"]
    print(type(pic))
    print('+++++++++++',pic.name,'+++++++')
    # pic.chunks()
    # 2.创建一个文件
    save_path = '%s/booktest/%s'%(settings.MEDIA_ROOT,pic.name)

    with open(save_path,'wb') as fp:
        # 3.获取上传文件的内容  并写到上传的文件中
        for content in pic.chunks():
            fp.write(content)
    # 4.在数据库中保存上传记录
    PicTest.objects.create(goods_pic='booktest/%s'%pic.name)
    # 5.返回
    return HttpResponse('ok')

# /show_area/页码
#前端访问的时候需要传递页码
def show_area(request,pindex):
    '''分页'''
    # 1.查询出所有省级地区的信息
    areas= AreaInfo.objects.filter(aParent__isnull=True)
    # 2.分页  每页显示10条
    paginator=Paginator(areas, 10)
    #返回总页数
    print("++++++++",paginator.num_pages,"++++++++")
    #返回总页码列表
    print("++++++++",paginator.page_range,"++++++++")
    # 3.获取第pindex页的内容
    # page是Page类的实例对象
    if pindex=='':
        # 默认取第一页的内容
        pindex=1
    else:
        pindex=int(pindex)
    page=paginator.page(pindex)
    #url正则匹配返回的都是字符串
    # 获取当前页的页码
    print('当前页的页码：',page.number,'+++++++++')
    # 4.使用模板
    # return render(request, 'booktest/show_area.html',{'areas':areas,'page':page})
    return render(request, 'booktest/show_area.html',{'page':page})

# /areas
def areas(request):
    '''省市县选中案例'''
    return render(request, 'booktest/areas.html')


# /prov
def prov(request):
    '''获取所有省级地区的信息'''
    # 1.获取所有省级地区的信息
    areas=AreaInfo.objects.filter(aParent__isnull=True)
    # 2.变量areas并拼接出json数据 ：atitle  id
    area_list=[]
    for area in areas:
        area_list.append((area.id,area.atitle))
    # 3.返回数据
    return JsonResponse({'data':area_list})

# /city
def city(request,pid):
    '''获取对应省下面的市的信息'''
    # 1.获取pid的下级地区的信息  下面的这两种方式都可以

    # AreaInfo.objects.get(id=pid)
    # areas=area.areainfo_set.all()

    areas=AreaInfo.objects.filter(aParent__id=pid)
    area_list=[]
    for area in areas:
        area_list.append((area.id,area.atitle))
    # 3.返回数据
    return JsonResponse({'data':area_list})
