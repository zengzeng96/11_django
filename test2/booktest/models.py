from django.db import models

# Create your models here.


class BookInfoManager(models.Manager):
    '''自定义图书模型管理类'''
    # Bookinfo.objects就是这个models.Manager的对象
    # pass
    # 1.改变查询的结果集

    def all(self):  # 重写父类的方法
        # 1.调用父类的all方法  获取所有的数据
        books = super(BookInfoManager, self).all()  # Query set
        # 2.对数据进行过滤
        books = books.filter(isDelete=False)
        # 3.返回查询集
        return books
    # 2.封装函数：操作模型类对应的数据表 一般不把操作函数写在模型类内部 这样就显得比较臃肿
    # 模型管理类好像有一个自己封装的create方法  用于创建新的模型类对象
    # BookInfo.objects.create(btitle='连城诀',bpub_date='1976-12-18')
    # 但是上面的这个方法调用的时候必须传入  关键字参数  必须是上面的这种写法 我们自己写的就不用  下面的
    # BookInfo.objects.create_book('雪山飞狐','1976-11-19')

    def create_book(self, btitle, bpub_date):
        # 默认的create方法 调用的时候必须通过关键字参数传参
        # 1.创建一个图书对象
        # 获取self所在的模型类
        model_class = self.model  # 这样就不怕模型类的名字改变了  
        #每一个模型管理器都具有一个model属性  就是他管理的是哪一个模型类
        # obj=BookInfo()
        obj = model_class()  # 创建一个模型类对象

        obj.btitle = btitle
        obj.bpub_date = bpub_date
        # 2.保存进数据库
        obj.save()
        # 3.返回obj
        return obj


# 一类
class BookInfo(models.Model):
    '''图书模型类'''
    # 图书名称
    btitle = models.CharField(max_length=20, db_column='title')
    # 图书价格  最大位数为10   小数位数为2
    # bprice=models.DecimalField(max_digits=10,decimal_places=2)#设置小数点的位数为2
    # 出版日期
    bpub_date = models.DateField()
    # 阅读数量
    bread = models.IntegerField(default=0)
    # 评论数量
    bcomment = models.IntegerField(default=0)
    # 逻辑删除  删除标记   不对数据库的值做真正的删除  删除的话该改为 True
    isDelete = models.BooleanField(default=False)

    # book=models.Manager()#自定义一个Manager类对象  没有什么卵用
    objects = BookInfoManager()
    # 这个objects不是django默认的objects  而是 我们自己定义的

    @classmethod
    def create_book(cls, btitle, bpub_date):  # 封装一个类方法 一般不把这个模型类封装在模型类的内部
        # 1.创建一个图书对象
        obj = cls()
        obj.btitle = btitle
        obj.bpub_date = bpub_date
        # 2.保存进数据库
        obj.save()
        # 3.返回obj
        return obj

    class Meta:
        db_table = 'bookinfo'  # 指定模型类对应的表名


# 多类
class HeroInfo(models.Model):
    '''英雄人物模型类'''
    # 英雄姓名
    hname = models.CharField(max_length=20)
    # 性别
    hgender = models.BooleanField(default=False)
    # 备注
    hcomment = models.CharField(max_length=200, null=True, blank=True)
    # blank 参数为True时 在后台管理的时候可以不用 输入内容进行保存
    # 为false时就必须输入
    # 关系属性   一对多 关系属性写在多类中
    hbook = models.ForeignKey('BookInfo')  # 一对多的关系
    # 逻辑删除  删除标记   不对数据库的值做真正的删除  删除的话该改为 True
    isDelete = models.BooleanField(default=False)


# ………………………………………………………………………………………………………………………………………………………………………………………………………………………………
'''
#新闻类型类
class NewsType(models.Model):
    # 类型
    type_name=models.CharField(max_length=20)
    # 关系属性   代表类型下面的信息
    type_news=models.ManyToManyField('NewsInfo')

# 这两者是多对多的关系 关系属性写在哪一个都可以

# 新闻类
class NewsInfo(models.Model):
    title=models.CharField(max_length=128)
    # 发布时间
    pub_date=models.DateTimeField(auto_now_add=True)#信息自动填充为新闻发布的时间
    # 信息内容
    content=models.TextField()
    # 关系属性  代表新闻所属的类型
    # news_type=models.ManyToManyField('NewsType')
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# 员工基本信息类
class EmployeeBasicInfo(models.Model):
    name=models.CharField(max_length=20)
    gender=models.BooleanField(default=False)
    age=models.IntegerField()
 
    # 关系属性  代表员工详细信息
    employee_detail=models.OneToOneField('EmployeeDetailInfo')

# 员工详细信息类
class EmployeeDetailInfo(models.Model):
    addr=models.CharField(max_length=256)
    education=models.TextField()

    # 关系属性  代表员工基本信息 一对一的关系  写在两个类中哪一个都可以
    employee_basic=models.OneToOneField('EmployeeBasicInfo')
'''
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


class AreaInfo(models.Model):
    # 他是一种特殊的一对多关系
    '''地区模型类'''
    # 地区名称
    atitle = models.CharField(max_length=20)
    # 关系属性，代表当前地区的父级地区
    aParent = models.ForeignKey('self', null=True, blank=True)
    # self  与自身有关联

    # class Meta:
    #     db_table = 'areas'
