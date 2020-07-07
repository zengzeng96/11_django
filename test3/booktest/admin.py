from django.contrib import admin
from booktest.models import AreaInfo,PicTest
# Register your models here.

class AreaStackedInline(admin.StackedInline):#块嵌入式
    """docstring for AreaStackedInline"""
    # 写多类的名字
    model=AreaInfo
    extra=2#新增的数量

class AreaTabularInline(admin.TabularInline):#列表式
    model=AreaInfo#
    extra=2#新增的数量
        

class AreaInfoAdmin(admin.ModelAdmin):
    """地区模型管理类"""
    list_per_page=10#指定每页显示10条数据
    list_display=['id','atitle','title','parent']
    #不仅可以写模型的属性 也可以写模型的方法

    actions_on_bottom=True#下拉列表在页面下方也有展示
    actions_on_top=False#下拉列表在页面上方不再展示
    list_filter=['atitle']#列表页右侧的过滤栏
    search_fields=['atitle']#列表页上方的搜索框

    # fields=['aParent','atitle']#定义字段的显示顺序
    fieldsets=(
        ('基本',{'fields':['atitle']}),
        ('高级',{'fields':['aParent']})
        )
    inlines=[AreaStackedInline]

admin.site.register(AreaInfo,AreaInfoAdmin)
admin.site.register(PicTest)
