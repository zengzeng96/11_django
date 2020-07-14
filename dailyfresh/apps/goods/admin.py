from django.contrib import admin
from goods.models import GoodsType, IndexPromotionBanner,IndexGoodsBanner,IndexTypeGoodsBanner,GoodsSKU
from django.core.cache import cache

class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        '''新增或更新表中的数据时调用'''
        super().save_model(request, obj, form, change)

        # 发出任务 让celery worker重新生成首页静态页
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        #清除首页的缓存数据
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """删除表中的数据"""
        super().delete_model(request, obj)

        # 发出任务 让celery worker重新生成首页静态页
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()
        # 清除首页的缓存数据
        cache.delete('index_page_data')

# Register your models here.
class GoodsTypeAdmin(BaseModelAdmin):
    pass

class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass

class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    list_display=['id','type_id','sku_id','index','display_type']

class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass
class GoodsSKUAdmin(BaseModelAdmin):
    list_display=['id','goods_id','type_id','price','unite','desc']

admin.site.register(GoodsType,GoodsTypeAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexTypeGoodsBanner,IndexTypeGoodsBannerAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)