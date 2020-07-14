from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.generic import View
from django_redis import get_redis_connection

from goods.models import (GoodsSKU, GoodsType, IndexGoodsBanner,
                          IndexPromotionBanner, IndexTypeGoodsBanner)
from order.models import OrderGoods


# Create your views here.
# http://127.0.0.1:8000
class IndexView(View):
    """首页"""

    def get(self, request):
        """显示首页"""
        # 尝试从缓存中获取数据
        context = cache.get('index_page_data')
        if context is  None:
            # 缓存中没有数据
            print("***" * 8, "设置缓存", "***" * 8)
            # 获取首页商品的种类信息
            types = GoodsType.objects.all()
            # 获取首页轮播商品信息
            goods_banner = IndexGoodsBanner.objects.all().order_by('index')  # 数字小的在前
            # for banner in goods_banner:
            #     print(banner.)
            # 获取首页促促销活动信息
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')
            # 获取首页商品分类商品展示信息
            # type_goods_banners = IndexTypeGoodsBanner.objects.all()
            for type in types:  # GoodsType对象
                # 获取type种类首页分类商品的有图片展示信息
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')

                # 动态给对象增加属性 分别保存首页分类展示的图片和文字展示信息
                type.image_banners = image_banners
                # 获取type种类首页分类商品的有文字展示信息
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
                type.title_banners = title_banners
                
            # 上面的信息都是一样的 为他们设置缓存
            context = {
                'types': types,
                'goods_banners': goods_banner,
                # 获取首页促促销活动信息
                'promotion_banners': promotion_banners}
            # 设置缓存
            # 传入的三个参数分别是  key   value     缓存时间
            cache.set('index_page_data', context, timeout=3600)  # 设置缓存的时间为3600秒

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated():
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            # 获取数据库中的购物车记录
            cart_count = conn.hlen(cart_key)
        # 组织模板上下文
        context.update(cart_count=cart_count)  # 更新字典 将数据加入字典
        print('%'*10,context['goods_banners'])
        return render(request, 'index.html', context=context)


# /goods/商品id
class DetailView(View):
    """详情页"""

    # 关于历史记录的添加
    def get(self, request, goods_id):
        """显示详情页"""
        try:
            sku = GoodsSKU.objects.get(id=goods_id)#在详情类商品查找详情商品
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return redirect(reverse('goods:index'))
        # 获取商品的分类信息
        print('*'*30,'商品详情页')
        types = GoodsType.objects.all()#商品的大类信息
        # 获取商品的评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')
        # 获取新品推荐  同一个大类  都是水果
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]  # 只获取两个新品推荐


        # 获取同一个SPU其他规格的商品   同一个中类   都是草莓
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)#同一个中类的商品 比如都是苹果
        # 红苹果 青苹果

        # 购物车
        user = request.user
        cart_count = 0
        if user.is_authenticated():
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            # 获取数据库中的购物车记录
            cart_count = conn.hlen(cart_key)
            # 用户登陆的情况下添加用户的历史浏览记录
            conn = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            # 移除列表中的goods_id
            conn.lrem(history_key, 0, goods_id)  # 0
            # 把goods_id插入到列表的左侧
            conn.lpush(history_key, goods_id)
            # 只保存用户最新的5条浏览记录
            conn.ltrim(history_key, 0, 4)

        # 组织模版上下文
        context = {
            'sku': sku,
            'types': types,
            'sku_orders': sku_orders,
            'new_skus': new_skus,
            'same_spu_skus': same_spu_skus,
            'cart_count': cart_count

        }
        # 使用模版
        return render(request, 'detail.html', context)


# 种类id   页码   排序方式
# restful api   --->请求一种资源
# /list?type_id=种类id&page=页码&sort=排序方式
# /list/种类id/页码/排序方式
# /list/种类id/页码?sort=排序方式 #我们在这里选择这种
class ListView(View):
    """列表页"""

    def get(self, request, type_id, page):
        '''显示列表页'''
        # 先获取种类的信息
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            # 种类不存在
            return redirect(reverse('goods:index'))
        # 获取商品的分类信息
        types = GoodsType.objects.all()
        # 获取排序的方式
        sort = request.GET.get('sort')

        # sort=price#按照价格排序
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        # sort=hot#按照销量排序
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:  # sort=default#默认按id顺序排序 其他的都按id进行排序
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')
        # 对数据进行分页
        paginator = Paginator(skus, 1)
        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1
        # 获取第page页的实例对象
        skus_page = paginator.page(page)
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

        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]  # 只获取两个新品推荐
        # 购物车记录
        user = request.user
        cart_count = 0
        if user.is_authenticated():
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            # 获取数据库中的购物车记录
            cart_count = conn.hlen(cart_key)
        # 阻止模版上下文
        context = {
            'types': types,
            'skus_page': skus_page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sort': sort,
            'pages': pages
        }

        return render(request, 'list.html', context)
