from django.db import models
# 设计和表对应的类  模型类
# Create your models here.


# 1类
# 图书类
class BookInfo(models.Model):

    '''图书模型类'''
    # CharField说明是一个字符串  max_length指定字符串的最大长度

    btitle = models.CharField(max_length=20)
    # if anaconda works just fine after you recieved this error and the
    # command above
    # 出版日期 DataField说明是一个日期类型
    bpub_date = models.DateField()

    def __str__(self):
        # 重写该方法 改变在网页后台中的显示
        return self.btitle  # 返回书名

    # 生成迁移文件
    '''
        python manage.py makemigrations
        迁移文件是根据模型类生成的
    '''
    # 执行迁移生成表
    '''
        python manage.py migrate
        默认的数据库 sqlite3 这是一个小型的数据库 用于手机端
        在linux下打开需要 sudo apt-get install sqliteman
        后面我们就不会用这个数据库了   而是用mysql数据库
        生成的数据库文件对应的表的名称是
        yunwenTest_bookinfo
        对应的应用名和models.py文件里定义的模型类的类名的小写
        应用名_类名小写
    '''
    # 进入django项目的shell
    '''
        python manage.py shell
        from yuwenTest.models import BookInfo
        b=BookInfo()
        b.btitle='天龙八部'
        from datetime import date
        b.bpub_date=date(1990,1,1)
        把实例属性添加到数据库
            b.save()

        查询数据库里具备一定条件的信息  假设查询 id=1
            b2=BookInfo.objects.get(id=1)
            type(b2)   返回的数据类型是 一个模型类的对象
            他就是一个类对象
            b2.btitle
            b2.bpub_date
        数据库对象的更新
            b2.bpub_date=date(1996,6,9)
            b2.save()#已经对应的有数据就是直接更新 没有的时候就是插入

        数据库对象的删除
            b2.delete()
            


    '''
# 多类
# 英雄人物类  一本图书包含多个英雄
'''
名字 hname
性别 hgender
年龄 hage
备注 hcomment
关系属性 建立图书类和英雄人物类之间的一对多关系 hbook

'''


class HeroInfo(models.Model):
    '''英雄人物类'''
    hname = models.CharField(max_length=20)
    # 性别 boolean 默认值为 False 代表男
    hgender = models.BooleanField(default=False)
    hcomment = models.CharField(max_length=128)

    # 关系属性
    # 关系属性对应的表的字段名格式：关系属性名_id
    hbook = models.ForeignKey('BookInfo')  # 建立一对多的关系
    '''
        h=HeroInfo()
        h.hname='段誉'
        h.hgender=False
        h.hcomment='六脉神剑'
        h.hbook=b
        h.save

        h2=HeroInfo()
        h2.hname='萧峰'
        h2.hgender=False
        h2.hcomment='降龙十八掌'
        h2.hbook=b
        h2.save()
        h3=HeroInfo.objects.get(id=2)
        h3.hbook.btitle

        b.heroinfo_set.all() 返回一个列表
        选择与b关联的HeroInfo类对象

        选择插入的所有对象
        BookInfo.objects.all()
        HeroInfo.objects.all()
    '''

    def __str__(self):
        #返回英雄的名字
        return self.hname
