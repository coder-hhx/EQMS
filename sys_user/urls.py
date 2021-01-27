from django.urls import path

from sys_user.views import *

urlpatterns = [
    path('area_mgr/', to_area_mgr),
    path('add_addr/', add_addr),
    path('edit_addr/', edit_addr),
    path('delete_addr/', delete_addr),
    path('all_mem_apply_for/', all_mem_apply_for),
    path('get_mem_materials/', get_mem_materials),
    path('rotate_pic/', rotate_pic),
    path('change_mem_status/', change_mem_status),
    path('search_mem_qualification/', search_mem_qualification),
    path('upload_compact/', upload_compact),
    path('delete_compact/', delete_compact),
    path('compact_mgr/', compact_mgr),
    path('download_compact/', download_compact),
    path('get_initiation_mem/', get_initiation_mem),
    path('activate_member/', activate_member),
    path('login/', to_login),
    path('logout/', to_logout),
    path('', to_area_mgr),
]
