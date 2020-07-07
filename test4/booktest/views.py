from django.shortcuts import render,redirect
from django.template import loader, RequestContext
from django.http import HttpResponse
from booktest.models import BookInfo

# Create your views here.
# def index(request):
#     '''使用模板文件'''
#     # 1.加载模板文件
#     temp=loader.get_template('booktest/index.html')
#     # 2.定义模板上下文 给模板文件传入数据
#     context=RequestContext(request,{})
#     # 3.模板渲染 产生一个替换后的html内容
#     res_html=temp.render(context)
#     # 4.返回应答
#     return HttpResponse(res_html)


def login_required(view_func):
    '''登录判断装饰器'''
    def wrapper(request,*view_args,**view_kwargs):
        # 判断用户是否登陆
        if request.session.has_key('islogin'):
            # 用户已经登陆 调用对应的视图
            return view_func(request,*view_args,**view_kwargs)
        else:
            return redirect('/login')

    return wrapper

# /index
def index(request):
    return render(request, 'booktest/index.html')


# /index2
def index2(request):
    ''' 模板文件的加载顺序 '''
    return render(request, 'booktest/index2.html')

# /temp_var
def temp_var(request):
    '''模板变量'''
    my_dict={'title':'字典键值'}
    my_list=[1,2,3]
    book=BookInfo.objects.get(id=1)
    # 定义模板上下文
    context={
        'my_dict':my_dict,
        'my_list':my_list,
        'book':book
    }
    return render(request,'booktest/temp_var.html',context=context)

# /temp_tags
def temp_tags(request):
    '''模板标签'''
    # 查找所有图书的信息
    books=BookInfo.objects.all()
    return render(request,'booktest/temp_tags.html',{'books':books})


def temp_filter(request):
    '''模板过滤器'''
    # 查找所有图书的信息
    books=BookInfo.objects.all()
    return render(request,'booktest/temp_filter.html',{'books':books})

# /temp_inherit
def temp_inherit(request):
    '''模板继承'''
    return render(request, 'booktest/child.html')

# /html_escape
def html_escape(request):
   '''html转义'''
   return render(request, 'booktest/html_escape.html',{'content':'<h1>hello</h1>'})


def login(request):
    '''显示登陆页面'''
    # 判断用户是否登陆
    if request.session.has_key('islogin'):
        #说明用户已经登陆 直接跳转到修改密码的页面
        return redirect('/change_pwd')
    else:
        # 说明用户未登陆
        # 获取cookie username
        if 'username' in request.COOKIES:
            # 获取记住的用户名
            username=request.COOKIES['username']
        else:
            username=''

        return render(request, 'booktest/login.html',{'username':username})



def login_check(request):
    username=request.POST.get('username')
    password=request.POST.get('password')
    remember=request.POST.get('remember')
    # 获取用户输入的验证码
    vcode1=request.POST.get('vcode')
    # 获取sesion中保存的验证码
    vcode2=request.session.get('verifycode')
    # 进行验证码校验
    if not vcode1==vcode2:
        # 验证码错误
        return redirect('/login')

    print('username:', username)
    print('password:', password)
    print('remember:',remember)
    # 2.进行校验
    # 实际开发 根据用户名和密码查找数据库
    #模拟 假设正确用户名： smart   正确密码：123
    if username=='smart' and password=='123':
        #用户名密码正确   跳转到修改密码的页面
        response=redirect('/change_pwd')#他的返回值就是一个httpResponseRedirect对象
        if remember=='on':
            # 设置cookie  username  过期时间为一周
            response.set_cookie('username',username,max_age=7*24*3600)
        #记住用户的登陆状态
        #只要session中有islogin  就认为用户已经登陆
        request.session['islogin']=True
        #记住登陆的用户名
        request.session['username']=username
        return response


# /change_pwd
@login_required
def change_pwd(request):
    '''显示修改密码页面'''
    # 进行用户是否登陆的判断
    # if not request.session.has_key('islogin'):
    #     #用户未登陆 跳转到登录页
    #     return redirect('/login')
    return render(request, 'booktest/change_pwd.html')


# /change_pwd_action
@login_required
def change_pwd_action(request):
    '''模拟密码修改处理'''
    # 进行用户是否登陆的判断
    # if not request.session.has_key('islogin'):
    #     #用户未登陆 跳转到登录页
    #     return redirect('/login')

    # 1.获取新密码
    pwd=request.POST.get('pwd')
    # 获取用户名
    username=request.session.get('username')
    # 2.实际开发的时候：修改对应数据库中的内容
    # 3.返回一个应答
    return HttpResponse('{}修改了密码为:{}'.format(username,pwd))

from PIL import Image, ImageDraw, ImageFont
from django.utils.six import BytesIO


# /verify_code
def verify_code(request):
    #引入随机函数模块
    import random
    #定义变量，用于画面的背景色、宽、高 RGB
    bgcolor = (random.randrange(20, 100), random.randrange(
        20, 100), 255)
    width = 100
    height = 25
    #创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    #创建画笔对象
    draw = ImageDraw.Draw(im)
    #调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    #定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    #随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    #构造字体对象，ubuntu的字体路径为“/usr/share/fonts/truetype/freefont”
    font = ImageFont.truetype('ubuntu.ttf', 23)
    #构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    #绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    #释放画笔
    del draw
    #存入session，用于做进一步验证
    request.session['verifycode'] = rand_str
    #内存文件操作
    buf = BytesIO()
    #将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    #将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')

# /url_reverse
def url_reverse(request):
    '''url反向解析页面'''
    return render(request, 'booktest/url_reverse.html')

def show_args(request,a,b):
    '''捕获位置参数'''
    return HttpResponse(a+':'+b)

def show_kwargs(request,c,d):
    '''捕获关键字参数'''
    return HttpResponse(c+':'+d)

from django.core.urlresolvers import reverse
# /test_redirect
def test_redirect(request):
    '''重定向到首页'''
    # 在视图中反向解析
    # url=reverse('booktest:index')#动态产生的重定向首页地址
    # 重定向到/show_args/1/2
    # url=reverse('booktest:show_args' ,args=(1,2))

    # 重定向到/show_kwargs/3/4
    url=reverse('booktest:show_kwargs' ,kwargs={'c':3,'d':4})
    return redirect(url)

