import re

from django.conf import settings
from django.contrib.auth import authenticate, login, logout  # 用于用户登录的校验和会话记录
from django.core.mail import send_mail  # 发邮件
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from django_redis import get_redis_connection
from itsdangerous import SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.core.paginator import Paginator
from celery_tasks.tasks import send_register_active_email
from goods.models import GoodsSKU
from user.models import Address, User
from utils.mixin import LoginRequiredMixin
from order.models import OrderInfo, OrderGoods


# Create your views here.

# /user/register


def register(request):
    """注册页面"""
    if request.method == "GET":
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
        user = User.objects.get(username=username)  # 只能返回一条且只能有一条满足条件的数据
    except User.DoesNotExist:
        # 用户名不存在
        user = None
    if user:
        # 说明用户名已存在
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
    # 发送激活邮件 包含激活链接：每个用户的激活链接不一致 http://127.0.0.1:8000/username/active/id
    # 把用户的身份信息进行加密
    # 激活链接中需要包含用户的激活信息
    # 加密用户的身份信息  生成激活token
    serializer = Serializer(settings.SECRET_KEY, 3600)  # 设置过期时间
    info = {'confirm': user.id}
    token = serializer.dumps(info)

    # 发送邮件

    return redirect(reverse('goods:index'))


class RegisterView(View):
    """注册"""

    def get(self, request):
        """显示注册页面"""
        return render(request, 'register.html')

    def post(self, request):
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
            user = User.objects.get(username=username)  # 只能返回一条且只能有一条满足条件的数据
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 说明用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0  # 用户刚注册的时候不应是激活的
        user.save()
        serializer = Serializer(settings.SECRET_KEY, 3600)  # 设置过期时间
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode('utf8')
        # **********************************发送邮件***************************************start
        # subject='天天生鲜欢迎信息'
        # message=''
        # sender=settings.EMAIL_FROM
        # print('*'*10,sender,'*'*10)
        # receiver=[email]
        # html_message='<h1>%s,欢迎您成为天天生鲜注册会员。</h1>请点击下面链接激活您的账户:<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>'%(username,token,token)
        # send_mail( subject,message,sender,recipient_list=receiver,html_message=html_message)
        send_register_active_email.delay(
            email, username, token)  # celery异步发送邮件
        # send_register_active_email.delay()#celery异步发送邮件
        # **********************************发送邮件***************************************end
        return redirect(reverse('goods:index'))  # 发出任务


class ActiveView(View):
    """用户激活"""

    def get(self, request, token):
        """进行用户激活"""
        # 进行解密，获取需要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)  # 设置过期时间
        # info={'confirm':user.id}
        try:
            info = serializer.loads(token)
            # 获取激活用户的id
            user_id = info['confirm']
            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 跳转到登录页面
            return redirect(reverse('user:login'))

        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')
            # 实际上应该再次发一个链接


class LoginView(View):  # 使用内置的函数进行校验
    """登录"""

    def get(self, request):
        """显示登录页面"""
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
            print('用户勾选了记住用户名', '#' * 40)
        else:
            username = ''
            checked = ''
        # 使用模版
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        """进行登录检验"""
        # 接受数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})
        # 校验数据
        # 业务处理
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request, user)
                # 获取登陆后所要跳转的地址 默认跳转到首页
                next_url = request.GET.get('next', reverse(
                    'goods:index'))  # 没有的话给一个默认值 设置他要跳转的地址
                # 跳转到首页
                response = redirect(next_url)
                # 判断是否需要记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    # 记住用户名
                    print('*' * 30, "记住用户名", '*' * 30)
                    response.set_cookie(
                        'username', username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie('username')
                # 返回应答
                return response
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


# /user/logout


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        # 清除用户的登录 session信息
        logout(request)
        # 跳转到首页
        return redirect(reverse("goods:index"))


# /user
class UserInfoView(LoginRequiredMixin, View):
    """用户中心-信息页"""

    def get(self, requset):
        '''显示'''
        # page='user'
        # request.user
        # 如果用户未登陆 --->AnonymousUser的一个实例
        # 如果用户未登陆 --->User的一个实例
        # request.user.is_authenticated()
        # 除了我们手动给模版传递的变量之外 django框架会把request.user也传给模版文件
        # 获取用户的个人信息
        user = requset.user
        address = Address.objects.get_default_address(user)

        # 获取用户的历史浏览记录
        # from redis import StrictRedis
        # sr=StrictRedis(host='192.168.176.132',port='6379',db=9)
        con = get_redis_connection('default')
        history_key = 'history_%d' % user.id
        # 获取用户最新浏览的5条商品的id
        sku_ids = con.lrange(history_key, 0, 4)
        # 从数据库中查询用户浏览的商品的具体信息
        # goods_li=GoodsSKU.objects.filter(id__in=sku_ids)
        goods_li = []
        # 遍历获取用户浏览的商品信息
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)
        # 组织上下文
        context = {'page': 'user',
                   'address': address,
                   'goods_li': goods_li}
        return render(requset, 'user_center_info.html', context=context)


# /user/order


class UserOrderView(LoginRequiredMixin, View):
    """用户中心-订单页"""

    def get(self, request, page):
        '''显示'''
        # 获取用户的订单信息
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')
        # 遍历获取订单的商品信息
        for order in orders:
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)
            # 遍历计算商品的小计
            for order_sku in order_skus:
                amount = order_sku.count * order_sku.price
                # 动态给order_sku增加amount属性
                order_sku.amount = amount
            #动态给对象增加属性 保存订单状态标题
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            # 动态给order增加属性，保存订单的商品信息
            order.order_skus = order_skus

        # 分页
        paginator = Paginator(orders, 1)
        # 处理页码
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1
        # 获取第page页的实例对象
        order_page = paginator.page(page)
        # todo:进行页码的控制 页面上最多显示5个页码
        # 1.总页数小于5页 页面上显示所有页码
        # 2.如果当前页是前三页的话   1 2 3 4 5
        # 3.如果当期页是后三页       n-4 n-3 n-2 n-1 n
        # 4.排除上面的三种情况 显示当前页的前两页 当前页的后两页
        num_pages = paginator.num_pages

        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)
        # 组织上下文
        context = {'order_page': order_page, 'pages': pages, 'page': 'order'}
        # 使用模板
        return render(request, 'user_center_order.html', context)


# /user/address


class AddressView(LoginRequiredMixin, View):
    """用户中心-地址页"""

    def get(self, request):
        '''显示'''
        # 获取用户的默认收货地址
        user = request.user
        # try:
        #     address=Address.objects.get(user=user,is_default=True)
        # except Address.DoesNotExist:
        #     #说明不存在默认收货地址
        #     address=None
        # 上面注释的代码等效于下面的一行  重写了地址模型类管理器对象
        address = Address.objects.get_default_address(user)
        return render(request, 'user_center_site.html', {'page': 'address', 'address': address})

    def post(self, request):
        '''地址的添加'''
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        # 校验数据
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机号码不正确'})
        # 业务处理
        # 获取登录用户对应的User对象
        user = request.user
        # try:
        #     address=Address.objects.get(user=user,is_default=True)
        # except Address.DoesNotExist:
        #     #说明不存在默认收货地址
        #     address=None
        address = Address.objects.get_default_address(user)
        if address:
            is_default = False
        else:
            is_default = True
        # 添加地址
        Address.objects.create(
            user=user,
            receiver=receiver,
            addr=addr,
            zip_code=zip_code,
            phone=phone,
            is_default=is_default
        )
        # 如果用户已存在默认收货地址 否则作为默认收货地址
        # 返回应答
        return redirect(reverse('user:address'))  # 重定向就是get请求方式
