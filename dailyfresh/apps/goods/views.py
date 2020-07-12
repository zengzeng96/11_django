from django.shortcuts import render
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django_redis import get_redis_connection


# Create your views here.
# http://127.0.0.1:8000
def index(request):
    """显示首页"""
    # 获取首页商品的种类信息
    types = GoodsType.objects.all()
    # 获取首页轮播商品信息
    goods_banner = IndexGoodsBanner.objects.all().order_by('index')  # 数字小的在前
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

    # 获取用户购物车中商品的数目
    user = request.user
    cart_count = 0
    if user.is_authenticated():
        # 用户已登录
        conn=get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 获取数据库中的购物车记录
        cart_count = conn.hlen(cart_key)

    # 组织模板上下文
    context = {
        'types': types,
        'goods_banner': goods_banner,
        # 获取首页促促销活动信息
        'promotion_banners': promotion_banners,
        # 获取首页商品分类商品展示信息
        # 'type_goods_banners' :type_goods_banners,
        # 获取用户购物车中商品的数目
        'cart_count': cart_count
    }
    return render(request, 'index.html', context=context)
