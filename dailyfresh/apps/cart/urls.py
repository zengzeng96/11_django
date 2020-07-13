from django.conf.urls import url
from cart.views import CartAppView,CartInfoView

urlpatterns = [
    url(r'^add/', CartAppView.as_view(),name='add'),#购物车记录添加
    url(r'^$', CartInfoView.as_view(),name='show'),#购物车页面显示
]