from django.urls import path
from django.urls import include
from .views import select_user,tree,create_user,delete_user,upload_single_file,download_single_file,get_usr_infor

urlpatterns = [
    path('select', select_user),
    path('^tree$',tree),
    path('signup',create_user),
    path('delaccount',delete_user),
    path('upload',upload_single_file),
    path('download',download_single_file),
    path('user_infor',get_usr_infor)
]