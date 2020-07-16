from django.conf.urls import url
# from user import views
from django.contrib.auth.decorators import login_required
from user.views import RegisterView,ActiveView, LoginView,UserInfoView,UserOrderView,AddressView,LogoutView
urlpatterns = [
    # url(r'^register$', views.register,name='register'),#FBV模式
    # url(r'^register_handle$', views.register_handle,name='register_handle'),
    url(r'^register$', RegisterView.as_view(),name='register'),#CBV模式
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(),name='active'),#用户激活
    url(r'^login$', LoginView.as_view(),name='login'),#登录
    # url(r'^$', login_required(UserInfoView.as_view()),name='user'),#用户中心信息页
    # url(r'^order$', login_required(UserOrderView.as_view()),name='order'),#用户中心订单页
    # url(r'^address$', login_required(AddressView.as_view()),name='address'),#用户中心地址页
    url(r'^$', UserInfoView.as_view(),name='user'),#用户中心信息页
    url(r'^order/(?P<page>\d+)$', UserOrderView.as_view(),name='order'),#用户中心订单页
    url(r'^address$', AddressView.as_view(),name='address'),#用户中心地址页
    url(r'^logout$', LogoutView.as_view(),name='logout'),#用户中心地址页
]