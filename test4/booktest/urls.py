from django.conf.urls import url
from booktest import views

urlpatterns = [
    url(r'^index3$', views.index,name='index'),
    url(r'^index2$', views.index2),  # 模板文件加载顺序
    url(r'^temp_var$', views.temp_var),  # 模板变量
    url(r'^temp_tags$', views.temp_tags),  # 模板变量
    url(r'^temp_filter$', views.temp_filter),  # 模板过滤器
    url(r'^temp_inherit$', views.temp_inherit),  # 模板继承
    url(r'^html_escape$', views.html_escape),  # html转义
    url(r'^login$', views.login),  # 显示登录页面
    url(r'^login_check$', views.login_check),  # 校验登录信息
    url(r'^change_pwd$', views.change_pwd),  # 显示修改密码页面
    # login_required(change_pwd)(request,*args,**kwargs)
    url(r'^change_pwd_action$', views.change_pwd_action),  # 显示修改密码页面
    url(r'^verify_code$', views.verify_code),  # 返回一个验证码图片
    url(r'^url_reverse$', views.url_reverse),  # url反向解析
    url(r'^test_redirect$', views.test_redirect),  # 在视图函数中重定向
    
    url(r'^show_args/(\d+)/(\d+)$', views.show_args,name='show_args'),  #捕获位置参数
    url(r'^show_kwargs/(?P<c>\d+)/(?P<d>\d+)$', views.show_kwargs,name='show_kwargs'),  #捕获关键字参数

]
