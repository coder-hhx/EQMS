#!/usr/bin/python3
# coding: utf-8
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect


def valid_login(view_func):
    sys_not_valid_paths = ['/sys/login/']
    mem_not_valid_paths = ['/mem/login/', '/mem/register/']

    def wrapper(request: HttpRequest, *args, **kwargs):
        # 验证当前请求是否在登录之后
        if all((
                'login_sys_user' not in request.session.keys(),
                request.path not in sys_not_valid_paths,
                request.path.startswith('/sys/')
        )):
            return redirect('/sys/login/')

        if all((
                'login_mem_user' not in request.session.keys(),
                request.path not in mem_not_valid_paths,
                request.path.startswith('/mem/')
        )):
            print('啦啦啦啦')
            return JsonResponse({'status': 302, 'msg': '请先登录！'})
        return view_func(request, *args, **kwargs)

    return wrapper
