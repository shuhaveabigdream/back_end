from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.http.response import StreamingHttpResponse
from django.views.decorators.http import require_http_methods
import json
import time
from .lib import path
from .lib import mysql_operation as mp
from .lib.addscrete import create_token,time_decode
file_admin=path.Path()#操作文件对象
db_operation=mp.mysql_operation()#操作数据库对象

def zip_pack(dict,cookies=None):
    response=JsonResponse(dict)
    if cookies:
        [response.set_cookie(k,v) for k,v in cookies.items()]
    return response

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
    if len(res)!=0:
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
    return zip_pack({'status':True},cookies={'token':user_token})
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
    #删除file表中所有记录
    file_obj=mp.file()
    db_operation.exceute_sql(sql=file_obj.delete(conditions={'belong':user_name}))
    return  zip_pack({'status':'True'})
@require_http_methods(['GET'])
def apply_token(requests):
    usr_name=requests.GET.get('usrName')
    if usr_name==None:
        return zip_pack({'status':False,'reason':'参数不匹配'})
    token_obj=mp.token()
    t_res=db_operation.select(sql=token_obj.select(conditions={'usr_name':usr_name}))
    if not t_res:
        return zip_pack({'status':False,'token':t_res[0][1]})
    return zip_pack({'status':True,'token':t_res[0][1]},cookies={'token':t_res[0][1]})
#method:GET
#fileName:string
#path:string
#t_batchs:int
#cur_batch:int
#content
#file_size文件总大小
@require_http_methods(['POST'])
def upload_single_file(requests):
    #检查用户信息
    token=requests.POST.get('token') if requests.COOKIES.get('token')==None else requests.COOKIES.get('token')
    content=requests.FILES.get('file',None)

    if not content:
        zip_pack({'status':False,'reason':'不存在文件'})
    if not token:
        return zip_pack({'status':False})
    token_obj=mp.token()
    usr_infor=db_operation.select(sql=token_obj.select(conditions={'token':token}))

    if len(usr_infor)==0:
        return zip_pack({'status':False,'reason':'用户不存在'})
    usr_Name=usr_infor[0][2]
    params=['fileName','path','t_batchs','cur_batch','file_size']

    vals=[requests.POST.get(key) for key in params]
    for val in vals:
        if val==None:
            return zip_pack({'status':False,'reason':'参数不匹配'})
    val_dict=dict(zip(params,vals))
    #文件冲突检查
    file_path = usr_Name + '/' + val_dict['path']
    abs_file_path=file_admin.show_path(file_path)
    file_obj = mp.file()
    res=db_operation.select(sql=file_obj.select(conditions={'file_path':abs_file_path}))
    if len(res)!=0 and res[0][7]==1:
        return zip_pack({'status':False})

    t_batchs=int(val_dict['t_batchs'])
    cur_batch=int(val_dict['cur_batch'])
    if t_batchs==1:#文件没有切割
        for item in content:#执行数据拷贝
            file_admin.write_sigle_chunk(file_path, item)
        #处理数据库
        file_obj.file_name=val_dict['fileName']
        file_obj.file_path=abs_file_path[:-1]
        file_obj.last_update=str(time.time())
        file_obj.belong=usr_Name
        file_obj.file_size=val_dict['file_size']
        file_obj.chunk=1
        file_obj.complete=True
        db_operation.exceute_sql(sql=file_obj.insert())
    else:#文件有进行切割
        if cur_batch==0:#文件创建
            file_obj.file_name = val_dict['fileName']
            file_obj.file_path = abs_file_path[:-1]
            file_obj.last_update = str(time.time())
            file_obj.belong = usr_Name
            file_obj.file_size = val_dict['file_size']
            file_obj.chunk = cur_batch
            file_obj.complete = False
            file_obj.file_name=val_dict['fileName']
            db_operation.exceute_sql(sql=file_obj.insert())
            for item in content:
                file_admin.write_sigle_chunk(file_path, item)
        else:#文件
            #检查当前批次是否正确
            file_res=db_operation.select(sql=file_obj.select(conditions={'file_path':abs_file_path[:-1]}))
            if len(file_res)==0:
                return zip_pack({'status':False,'reason':'文件不存在'})
            else:
                chunk=file_res[0][-2]
                if chunk+1!=cur_batch:
                    return zip_pack({'status':False,'reason':'批次不正确'})
            for item in content:
                file_admin.write_sigle_chunk(file_path, item)
            up_data={}
            up_data['chunk']=cur_batch
            if cur_batch+1==t_batchs:
                db_operation.exceute_sql(sql=file_obj.update(conditions={'file_path': abs_file_path[:-1]}, kwargs={'complete': 1}))
            db_operation.exceute_sql(sql=file_obj.update(conditions={'file_path':abs_file_path[:-1]},kwargs={'chunk':cur_batch}))
    return zip_pack({'status':True})
#method:GET
#path:string
#token
@require_http_methods(['GET'])
def download_single_file(requests):
    #检查参数
    token = requests.GET.get('token') if requests.COOKIES.get('token') == None else requests.COOKIES.get('token')
    path=requests.GET.get('path')
    if token ==None or path ==None:
        return zip_pack({'status':False,'reason':'参数不匹配'})

    token_obj = mp.token()
    usr_infor = db_operation.select(sql=token_obj.select(conditions={'token': token}))
    if len(usr_infor) == 0:
        return zip_pack({'status': False, 'reason': '用户不存在'})
    usr_Name = usr_infor[0][2]
    abs_file_path = file_admin.show_path(usr_Name +'/' + path)  # 获取完整路径

    #检查文件
    file_obj=mp.file()
    file_res = db_operation.select(sql=file_obj.select(conditions={'file_path': abs_file_path,'belong':usr_Name}))
    if len(file_res)==0 or file_res[0][-1]==0:
        return zip_pack({'status':False,'reason':'文件不存在或未完成'})

    fileName=file_res[0][1]
    #文件流下载
    def file_iterator(path, chunk_size=1024):
        with open(path[:-1], 'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    response = StreamingHttpResponse(file_iterator(abs_file_path), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(fileName)
    return response

#用于查询该目录的数据
@require_http_methods(['GET'])
def Get_Layer(requests):
    token = requests.GET.get('token') if requests.COOKIES.get('token') == None else requests.COOKIES.get('token')
    path=requests.GET.get('path')
    if token ==None or path ==None:
        return zip_pack({'status':False,'reason':'参数不匹配'})
    token_obj = mp.token()
    usr_infor = db_operation.select(sql=token_obj.select(conditions={'token': token}))
    if len(usr_infor) == 0:
        return zip_pack({'status': False, 'reason': '用户不存在'})
    usr_Name = usr_infor[0][2]
    relative_path=usr_Name+'/'+path
    res=file_admin.package_One_layer(relative_path)
    if res:
        return zip_pack(res)
    else:
        return zip_pack({'status':False,'reason':'非法路径'})

#删除文件/文件夹
#增加文件夹
#method:post
#params:
#path:
#token
#operation:add/delete
def dir_operation(requests):
    # 检查参数
    token = requests.POST.get('token') if requests.COOKIES.get('token') == None else requests.COOKIES.get('token')
    path = requests.POST.get('path')
    if token == None or path == None:
        return zip_pack({'status': False, 'reason': '参数不匹配'})

    token_obj = mp.token()
    usr_infor = db_operation.select(sql=token_obj.select(conditions={'token': token}))
    if len(usr_infor) == 0:
        return zip_pack({'status': False, 'reason': '用户不存在'})
    usr_Name = usr_infor[0][2]
    op=requests.POST.get('operation')
    file_obj=mp.file()
    if op==None:
        return zip_pack({'status':False,'reason':'没有操作'})
    if op=='add':
        file_admin.add_dirctionary(usr_Name+'/'+path)
        return zip_pack({'status':True})
    if op=='delete':
        all_files=file_admin.get_all_file(usr_Name + '/' + path)
        print(all_files)
        for file in all_files:
            db_operation.exceute_sql(sql=file_obj.delete(conditions={'file_path':file}))
        status = file_admin.remove(usr_Name + '/' + path)
        if status == False:
            return zip_pack({'status':False,'reason':'路径不合法'})
        else:
            #数据删除操作
            #返回
            return zip_pack({'status':True})



