import re

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from itsdangerous import SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.core.mail import send_mail#发邮件
from user.models import User
from celery_tasks.tasks import send_register_active_email
# Create your views here.

# /user/register


def register(request):
    """注册页面"""
    if request.method=="GET":
        """显示注册页面"""
        return render(request, 'register.html')
    else:
        return register_handle(request)




def register_handle(request):
    """进行注册处理  不使用这个函数了 使用类了"""
    # 接收数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')
    allow = request.POST.get('allow')
    # username=request.POST.get('user_name')
    # 进行数据校验
    if not all([username, password, email]):  # 列表里的数据都为真的时候才返回真
        return render(request, 'register.html', {'errmsg': '数据不完整'})

    # 校验邮箱re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

    if allow != 'on':
        return render(request, 'register.html', {'errmsg': '请同意协议'})
    
    # 校验用户名是否重复
    try:
        user=User.objects.get(username=username)#只能返回一条且只能有一条满足条件的数据
    except User.DoesNotExist:
        #用户名不存在
        user=None
    if user:
        #说明用户名已存在
        return render(request, 'register.html', {'errmsg': '用户名已存在'})

    # 进行业务处理：进行用户注册
    user = User.objects.create_user(username, email, password)
    user.is_active = 0  # 用户刚注册的时候不应是激活的
    user.save()

    # user=User()
    # user.username=username
    # user.password=password
    # user.email=email
    # user.save()
    # 返回应答 跳转到首页
    #发送激活邮件 包含激活链接：每个用户的激活链接不一致 http://127.0.0.1:8000/username/active/id
    # 把用户的身份信息进行加密
    # 激活链接中需要包含用户的激活信息
    # 加密用户的身份信息  生成激活token
    serializer=Serializer(settings.SECRET_KEY,3600)#设置过期时间
    info={'confirm':user.id}
    token=serializer.dumps(info)

    #发送邮件






    return redirect(reverse('goods:index'))

class RegisterView(View):
    """注册"""
    def get(self,request):
        """显示注册页面"""
        return render(request,'register.html')
    def post(self,request):
        """进行注册处理"""
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # username=request.POST.get('user_name')
        # 进行数据校验
        if not all([username, password, email]):  # 列表里的数据都为真的时候才返回真
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})
        
        # 校验用户名是否重复
        try:
            user=User.objects.get(username=username)#只能返回一条且只能有一条满足条件的数据
        except User.DoesNotExist:
            #用户名不存在
            user=None
        if user:
            #说明用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0  # 用户刚注册的时候不应是激活的
        user.save()
        serializer=Serializer(settings.SECRET_KEY,3600)#设置过期时间
        info={'confirm':user.id}
        token=serializer.dumps(info)
        token=token.decode('utf8')
        # **********************************发送邮件***************************************start
        # subject='天天生鲜欢迎信息'
        # message=''
        # sender=settings.EMAIL_FROM
        # print('*'*10,sender,'*'*10)
        # receiver=[email]
        # html_message='<h1>%s,欢迎您成为天天生鲜注册会员。</h1>请点击下面链接激活您的账户:<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>'%(username,token,token)
        # send_mail( subject,message,sender,recipient_list=receiver,html_message=html_message)
        send_register_active_email.delay(email,username,token)#celery异步发送邮件
        # **********************************发送邮件***************************************end
        return redirect(reverse('goods:index'))#发出任务

class ActiveView(View):
    """用户激活"""
    def get(self,request,token):
        """进行用户激活"""
        #进行解密，获取需要激活的用户信息
        serializer=Serializer(settings.SECRET_KEY,3600)#设置过期时间
        # info={'confirm':user.id}
        try:
            info=serializer.loads(token)
            #获取激活用户的id
            user_id=info['confirm']
            #根据id获取用户信息
            user=User.objects.get(id=user_id)
            user.is_active=1
            user.save()
            #跳转到登录页面
            return redirect(reverse('user:login'))

        except SignatureExpired as e:
            #激活链接已过期
            return HttpResponse('激活链接已过期')
            #实际上应该再次发一个链接

class LoginView(View):
    """登录"""
    def get(self,request):
        """显示登录页面"""
        return render(request,'login.html')
