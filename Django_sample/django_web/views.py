from django.shortcuts import render
from django_web.models import ArticleInfo
from django.core.paginator import Paginator


# Create your views here.
def index(request):
    limit=4

    arti_info = ArticleInfo.objects[:20]  # 是一个列表 但是只有一个元素
    paginator=Paginator(arti_info,limit)
    page=request.GET.get('page',1)
    print("*"*60)
    print(request)
    print(request.GET)
    print("*"*60)
    loaded=paginator.page(page)
    # context = {
    #     'title': arti_info[0].movie_name,
    #     'des': arti_info[0].describe,
    #     'score': arti_info[0].star
    # }
    context = {
        'ArtiInfo': loaded
    }
    return render(request, 'index.html', context)
