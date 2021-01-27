from django.urls import path

from mem_user.views import *

urlpatterns = [
    path('apply_for_qualification/', apply_for_qualification),
    path('get_compact/', get_compact),
    path('login/', login),
    path('register/', register),
    path('change_pwd/', change_pwd),
    path('get_area/', get_area),
    path('upload_pic/', upload_pic),
    path('download_compact/', download_compact),
    path('get_qualification/', get_qualification)
]
