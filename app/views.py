from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import json
import time
from .lib import path
from .lib import mysql_operation as mp
from .lib.addscrete import create_token,time_decode
file_admin=path.Path()#操作文件对象
db_operation=mp.mysql_operation()#操作数据库对象

def zip_pack(dict):
    return HttpResponse(json.dumps(dict),content_type='application/json')

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]#所以这里是真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')#这里获得代理ip
    return ip

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

#method post
#usrName string
#return:
# staus
# reason if staus is False
@require_http_methods(['POST'])
def create_user(requests):
    userName=requests.POST.get('usrName')
    if userName==None:
        return zip_pack({'status':False,'reason':'请求参数错误'})

    user_token=create_token(userName)
    cur_time=time.time()
    #添加user词条
    usr=mp.user()
    #查询是否存在该用户
    res=db_operation.select(sql=usr.select(conditions={'usrName':userName}))
    if res:
        return zip_pack({'status':False,'reason':'用户已存在'})
    usr.usrName=userName
    usr.last_login_date=cur_time
    usr.last_login_addr=get_ip(requests)
    usr.path=file_admin.show_path(userName)
    if db_operation.exceute_sql(sql=usr.insert())==False:
        return zip_pack({'status':False,'reason':'请联系管理员'})
    #添加token词条
    m_token=mp.token()
    m_token.usr_name=userName
    m_token.tokenVal=user_token
    if db_operation.exceute_sql(sql=m_token.insert())==False:
        return zip_pack({'status':False,'reason':'请联系管理员'})
    #创建文件夹
    file_admin.add_dirctionary(path=userName)  # 创建文件夹
    return zip_pack({'status':True})
#删除用户
#usrName
#return:
#status: True False
#reason: if status is False
@require_http_methods(['GET'])
def get_usr_infor(requests):
    user_name=requests.GET.get('usrName')
    usr=mp.user()
    res=db_operation.select(sql=usr.select(conditions={'usrName':user_name}))
    return zip_pack({'status':True,'data':res})

@require_http_methods(['POST'])
def delete_user(requests):
    user_name=requests.POST.get('usrName')
    if user_name==None:
        return zip_pack({'status':False,'reason':'参数不匹配'})
    usr=mp.user()
    m_token=mp.token()
    res=db_operation.select(sql=usr.select(conditions={'usrName':user_name}))
    if not res:
        return zip_pack({'status':False,'reason':'用户不存在'})
    #删除文件夹
    file_admin.remove_directory(user_name)
    #删除user表中记录
    if db_operation.exceute_sql(sql=usr.delete(conditions={'usrName':user_name}))==False:
        return zip_pack({'status':False,'reason':'请联系管理员'})
    #删除token表中记录
    if db_operation.exceute_sql(sql=m_token.delete(conditions={'usr_name': user_name}))==False:
        return zip_pack({'status':False,'reason':'请联系管理员'})
    return  zip_pack({'status':'True'})
def apply_token(requests):
    pass

def upload_single_file(requests):
    pass

def download_single_file(requets):
    pass

