import os
import sys
import configparser
import shutil
from functools import reduce
from django.conf import settings
'''
api总结
write_sigle_file       params:path,content
read_sigle_file        params:path  callbacks:content
add_directory          params:path
tree                   params:path callbacks:an array of files
getInfor               params:path callbacks:an array of detail about files
remove_sigle_file      params:path
remove_directory       params:path
div_chunks             params:content,package,batch
combine_chunks         params:path target_path
combin_chunks_nocache  params:path target_path
'''

class Path:
    def __init__(self,config_path='./app/lib/config.ini'):
        if __name__=="__main__":
            config_path='./config.ini'
        config=configparser.ConfigParser()
        config.read(config_path)
        self.basePath=config.get('PATH','BASE_PATH').replace("'",'')
        self.filePath=config.get('PATH','FILE_PATH').replace("'",'')
    def add_dirctionary(self,path=None):
        print(settings.BASE_DIR)
        myPath=self.filePath+('' if path==None else path)
        if not os.path.exists(myPath):
            os.mkdir(myPath)
        else:
            raise Exception("该位置不合法",myPath)
    def read_sigle_file(self,path,batchs=None):
        with open(self.filePath+path,'rb') as f:
            content=f.read()
        f.close()
        return content
    def write_sigle_file(self,path,content,batchs=None):
        with open(self.filePath+path,'wb') as f:
            f.write(content)
        f.close()
        return
    def tree(self,path=None):
        path = self.filePath + (path if path != None else '')
        if os.path.isdir(path):
            for root,subdict,files in os.walk(path):
               return root,subdict,files
        else:
            return path,[],['']
    def getInfor(self,path=None,relative=True):
        if relative:
            path = self.filePath+ (path if path != None else '')
        fileinfor=os.stat(path)
        file_size=fileinfor.st_size
        last_visit_data=fileinfor.st_atime
        last_change_date=fileinfor.st_mtime
        filepath, tmpfile = os.path.split(path)
        shortname, extension = os.path.splitext(tmpfile)
        return {
                'file_name':shortname,
                'extend_name':extension,
                'file_size':file_size,
                'last_visit':last_visit_data,
                'last_change':last_change_date
        }
    def remove_sigle_file(self,path):
        if os.path.exists(path):
            os.remove(path)
            return True
        else:
            return False
    def remove_directory(self,path,relative=True):
        if relative:
            path = self.filePath + (path if path != None else '')
        shutil.rmtree(path+'/')
        return True
    def get_all_file(self,path):
        path = self.filePath + (path if path != None else '')
        buf=[]
        def walk_File(file):
            for root, dirs, files in os.walk(file):
                for f in files:
                    buf.append(root+'/'+f)
                for d in dirs:
                    walk_File(root+'/'+d)
        walk_File(path)
        return buf
    def remove(self,path):
        path = self.filePath + (path if path != None else '')
        if not os.path.exists(path):
            return False
        if os.path.isdir(path):
            self.remove_directory(path,False)
        else:
            self.read_sigle_file(path)
        return True
    #大文件的切割与合并
    def div_chunks(self,content,package,batch_size=32):
        self.add_dirctionary(package)
        fileName='Batch_'
        chunk_size=len(content)//batch_size
        for i in range(0,batch_size-1):
            sub_content=content[i*chunk_size:(i+1)*chunk_size]
            self.write_sigle_file(package+'/'+fileName+str(i),sub_content)
        last_batch=content[(batch_size-1)*chunk_size:]
        self.write_sigle_file(package+'/'+ fileName+str(batch_size-1),last_batch)
        return True
    def combine_chunks(self,path,target_path):
        path = self.filePath + (path if path != None else '')
        files=os.listdir(path)
        indexs=sorted(files,key=lambda x:int(x.split('_')[1]))
        callback_file=b''
        for item in indexs:
            callback_file+=open(path+'/'+item,'rb').read()
        self.write_sigle_file(target_path,callback_file)
        return True
    def combin_chunks_nocache(self,path,target_path):
        path = self.filePath + (path if path != None else '')
        files=os.listdir(path)
        indexs=sorted(files,key=lambda x:int(x.split('_')[1]))
        with open(target_path,'ab+') as f:
            for index in indexs:
                ct=open(path+'/'+index,'rb').read()
                f.write(ct)
        f.close()
    def write_sigle_chunk(self,path,content):
        path = self.filePath + (path if path != None else '')
        with open(path,'ab+') as f:
            f.write(content)
        f.close()
        return True
    def package_One_layer(self,path=None):
        if os.path.exists(self.filePath + (path if path != None else '')):
            pwd,subdirec,files=self.tree(path)
            ans=[self.getInfor(path+'/'+item) if item!='' else self.getInfor(path) for item in files]
            callback={
                        'files_infor':ans,
                        'subdirecs':subdirec
                      }
            return callback
        else:
            return False
    def show_path(self,path):
        return self.filePath + (path if path != None else '')+'/'

if __name__=="__main__":
    obj=Path()
    print(obj.show_path('userName'))