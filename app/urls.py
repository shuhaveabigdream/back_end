from django.urls import path
from django.urls import include
from .views import select_user,tree

urlpatterns = [
    path('select', select_user),
    path('^tree$',tree)
]