import pymysql
from functools import wraps
import time

def logging(func):
    @wraps(func)
    def wrapped_function(*args,**kwargs):
        cur_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        record='sql:%s \nstatus %s \ntime:%s\r\n'
        sql_sen=kwargs['sql']
        status=func(*args,**kwargs)
        encode_status='success' if status!=False else 'fail'
        with open('./log','a+') as f:
            f.write(record%(sql_sen,encode_status,cur_time))
        f.close()
        return status
    return wrapped_function

class model:
    def __init__(self):
        pass
    def insert(self):
        pass
    def delete(self,conditions):
        con_array=list(conditions.items())
        return 'delete from  '+self.db+ ' where ' +' and '.join(["%s='%s'"%item for item in con_array])
    def update(self,conditions,kwargs):
        return "update " +self.db+ " set %s='%s'"%list(kwargs.items())[0]+' where '+' and '.join(["%s='%s'"%item for item in list(conditions.items())])
    def select(self,conditions=None):
        return 'select * from  ' +self.db+ 'where ' + ' and '.join(["%s='%s'" % item for item in list(conditions.items())]) if conditions!=None else\
        'select * from '+self.db


class user(model):
    def __init__(self):
        self.usrName=''
        self.path=''
        self.last_login=''
        self.db='user_list'
        super(user,self).__init__()
    def insert(self):
        return 'insert into '+self.db+'(usrName,path,last_login) values (\'%s\',\'%s\',\'%s\')'%(self.usrName,self.path,self.last_login)

class token(model):
    def __init__(self):
        self.tokenVal = ''
        self.create_time = ''
        self.usr_name = ''
        self.db='token_list'
        super(token,self).__init__()
    def insert(self):
        return 'insert into '+self.db +'(token,create_time,usr_name) values (\'%s\',\'%s\',\'%s\')' % (
        self.tokenVal, self.create_time, self.usr_name)

class file(model):
    def __init__(self):
        self.file_name=''
        self.file_size=''
        self.belong=''
        self.last_update=''
        self.file_path=''
        self.db='file_list'
        super(file,self).__init__()
    def insert(self):
        return 'insert into ' + self.db + '(file_name,file_size,belong,last_update,file_path) values (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')' % (
            self.file_name, self.file_size, self.belong,self.last_update,self.file_path)
class mysql_operation:
    def __init__(self,user='root',password='Shu@123456',db='diskdb',log_dir='./log'):
        self.conn=pymysql.connect(host='localhost',
                                  user=user,
                                  password=password,
                                  db=db)
        self.log_dir=log_dir
    @logging
    def exceute_sql(self,sql):
        try:
            self.conn.cursor().execute(sql)
            self.conn.commit()
            return True
        except Exception as e:
            print(e, sql)
            return False
    @logging
    def select(self,sql):
        try:
            cursor=self.conn.cursor()
            cursor.execute(sql)
            content=cursor.fetchmany(5)
            return content
        except Exception as e:
            print(e,sql)
            return False
    def customer_establish(self):
        sql_create_usr = "create table user_list(\
            usr_id int unsigned auto_increment,\
            usrName varchar(20) not null,\
            path varchar(50) not null,\
            last_login varchar(60),\
            primary key(usr_id))ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        sql_create_token = "create table token_list(\
            token_id int unsigned auto_increment,\
            token varchar(100) not null,\
            usr_name varchar(20) not null,\
            create_time varchar(20) not null,\
            primary key(token_id))ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        sql_create_file = "create table file_list(\
            file_id int unsigned auto_increment,\
            file_name varchar(40) NOT NULL,\
            file_size varchar(20) NOT NULL,\
            belong varchar(40),\
            last_update varchar(40) NOT NULL,\
            file_path varchar(100) NOT NULL,\
            PRIMARY KEY(file_id))ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        self.exceute_sql(sql=sql_create_usr)
        self.exceute_sql(sql=sql_create_file)
        self.exceute_sql(sql=sql_create_token)
        print('establish complete')


if __name__=="__main__":
    obj=mysql_operation()
    '''t=user()
    t.usrName='testuser'
    t.path='./path'
    t.last_login='2020/7/11'
    print(t.insert())
    print(t.update({'usrName':'dashen'},{'usrName': 'zhouke','id':'1001'}))
    print(t.delete({'usrName':'aka'}))
    print(t.select({'id':'1001'}))

    print('=============================')

    obj.exceute_sql(sql=t.insert())
    print(obj.select(sql=t.select()))
    obj.exceute_sql(sql=t.update({'usrName':'testuser'},{'usrName':'akali'}))
    print(obj.select(sql=t.select()))
    obj.exceute_sql(sql=t.delete({'usrName':'akali'}))
    print(obj.select(sql=t.select()))'''
    t=file()
    t.file_path='TSVM.pdf'
    t.file_size='0.68mb'
    t.belong='zhouke'
    t.last_update='2020:7:10'
    t.file_path='./file/zhouke/TSVM.pdf'
    obj.exceute_sql(sql=t.insert())
    print(obj.select(sql=t.select()))
    obj.exceute_sql(sql=t.update({'belong': 'zhouke'}, {'belong': 'akali'}))
    print(obj.select(sql=t.select()))
    obj.exceute_sql(sql=t.delete({'belong': 'akali'}))
    print(obj.select(sql=t.select()))
