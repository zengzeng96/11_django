from django.contrib import admin
from booktest.models import AreaInfo,PicTest
# Register your models here.
# 注册模型类
# 用户名  admin    密码：123456
class AreaStackedInline(admin.StackedInline):#块嵌入式
    """docstring for AreaStackedInline"""
    # 写多类的名字
    model=AreaInfo
    extra=2#新增的数量  控制有几个空行

class AreaTabularInline(admin.TabularInline):#列表式
    model=AreaInfo#
    extra=2#新增的数量
        

class AreaInfoAdmin(admin.ModelAdmin):
    """地区模型管理类"""
    list_per_page=10#指定每页显示10条数据
    list_display=['id','atitle','title','parent']
    #不仅可以写模型的属性 也可以写模型的方法 上面的title就是在模型类里写的一个方法

    actions_on_bottom=True#下拉列表在页面下方也有展示
    actions_on_top=False#下拉列表在页面上方不再展示
    list_filter=['atitle']#列表页右侧的过滤栏  可以写多个
    search_fields=['atitle']#列表页上方的搜索框

    # fields=['aParent','atitle']#定义字段的显示顺序
    # field和fieldsets这两个属性只能用一个 不能两个同时用
    fieldsets=(
        ('基本',{'fields':['atitle']}),
        ('高级',{'fields':['aParent']})
        )
    inlines=[AreaStackedInline]

admin.site.register(AreaInfo,AreaInfoAdmin)#模型类的注册
admin.site.register(PicTest)
