
from django.conf.urls import url

from booktest import views

urlpatterns = [
    url(r'^index$', views.index),#首页
    url(r'^index01$', views.index01),#首页测试ajax
    # url(r'^showarg(\d+)$', views.show_arg),#捕获url  位置参数
    url(r'^showarg(?P<num>\d+)$', views.show_arg),#捕获url  关键字参数
    url(r'^login$', views.login),#显示登录页面
    url(r'^login_check$', views.login_check),#显示登录校验页面 
    # 第一次做会出错  注释setting中的第47行  'django.middleware.csrf.CsrfViewMiddleware'
    url(r'^test_ajax$', views.ajax_test),#显示ajax页面
    url(r'^ajax_handle$', views.ajax_handle),#ajax处理
    url(r'^login_ajax$', views.login_ajax),#显示ajax登录
    url(r'^login_ajax_check$', views.login_ajax_check),#ajax登录校验

    url(r'^set_cookie$', views.set_cookie),#设置cookie
    url(r'^get_cookie$', views.get_cookie),#获取cookie

    url(r'^set_session$', views.set_session),#设置session
    url(r'^get_session$', views.get_session),#获取session
    url(r'^clear_session$', views.clear_session),#清除session
    url(r'^static_test$', views.static_test),#静态文件
    url(r'^show_upload$', views.show_upload),#显示上传图片
    url(r'^upload_handle$', views.upload_handle),#显示上传图片
    url(r'^show_area(?P<pindex>\d*)$', views.show_area),#显示上传图片
    url(r'^areas$', views.areas),#省市县选择案例
    url(r'^prov$', views.prov),#省级地区信息
    url(r'^city(\d+)$', views.city),#获取市级地区信息
    url(r'^dis(\d+)$', views.city),#获取县级地区信息

]
