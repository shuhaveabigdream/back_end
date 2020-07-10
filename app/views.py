from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from .lib import path

file_admin=path.Path()

@require_http_methods(['GET'])
def select_user(requests):
    userName=requests.GET.get('usr')
    #check userName
    #requests.COOKIES['token']=
    return HttpResponse('<h1>%s<h1>'%userName)
@require_http_methods(['GET'])
def tree(requests):
    cookies=requests.COOKIES
    ans=''
    if cookies.get('token'):
        ans=cookies.get('token')
    else:
        ans='can\'t find the token'
    return HttpResponse('<h1>%s<h1>'%ans)
