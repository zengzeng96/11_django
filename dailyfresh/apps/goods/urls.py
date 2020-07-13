from django.conf.urls import url
from goods import views
from goods.views import IndexView,DetailView,ListView
urlpatterns = [
    url(r'^index$', IndexView.as_view(),name='index'),
    url(r'^detail/(?P<goods_id>\d+)$', IndexView.as_view(),name='detail'),#详情页
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)$', ListView.as_view(),name='list'),#详情页
]