from django.urls import path, include

urlpatterns = [
    path('sys/', include('sys_user.urls')),
    path('mem/', include('mem_user.urls')),
]
