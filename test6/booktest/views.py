from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def set_session(request):
    '''设置session'''
    request.session['username'] = 'zengjia'
    request.session['age'] = 24
    return HttpResponse('设置session')

def get_session(request):
    '''设置session'''
    username=request.session['username']
    age=request.session['age']
    return HttpResponse(username+":"+str(age))

def index(request):
    user_ip=request.META['REMOTE_ADDR']
    print(user_ip)
    return HttpResponse('远端浏览器的ip'+user_ip)