import os
import re
import urllib

from django.http import JsonResponse, FileResponse

from sys_user.models import Members, MemberMaterials, AreaAddr
from log_util import log
from common import make_pwd, BASE_DIR


def login(request):
    """
    登录页
    :param request:
    :return:
    """
    if request.method == 'POST':
        # 获取用户名和口令
        name = request.POST.get('username', '')
        pwd = request.POST.get('password', '')

        if any((not name, not pwd, len(name) == 0, len(pwd) == 0)):
            msg = '用户名或口令不能为空！'
            status = 400
        else:
            try:
                ret = Members.objects.filter(name=name, auth_str=make_pwd(pwd))
                if ret.exists():
                    login_user = ret.first()

                    if login_user.activate == 1:
                        # 将登陆的用户信息存在session中
                        request.session['login_mem_user'] = {
                            'id': login_user.id,
                            'name': login_user.name
                        }
                        return JsonResponse({
                            'status': 200,
                            'msg': '登录成功！',
                            'data': {
                                'id': login_user.id
                            }
                        })
                    else:
                        msg = '您的会员申请尚未通过，请与后台管理员联系！'
                        status = 400
                else:
                    msg = '用户名或密码错误'
                    status = 400
            except Exception as e:
                log.error('用户登录失败：' + str(e))
                msg = '登录失败！'
                status = 400

        return JsonResponse({'status': status, 'msg': msg})


def register(request):
    """
    会员申请
    :param request:
    :return:
    """
    if request.method == 'POST':
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        if any((not name, not phone, len(name) == 0, len(phone) == 0)):
            log.error('申请会员失败：名字或电话号码不能为空')
            msg = '用户名或手机号不能为空'
            status = 400
        else:
            ret = re.match(r"^1[3456789]\d{9}$", phone)
            if not ret:
                msg = '手机号格式错误'
                status = 400
            else:
                try:
                    if Members.objects.filter(phone=phone).exists():
                        return JsonResponse({'status': 400, 'msg': '该手机号已绑定会员账号，请更换手机号或直接登录！'})
                    Members.objects.create(name=name, phone=phone, auth_str=(make_pwd(phone[-6:])))
                    status = 200
                    msg = '申请成功，您的初始密码为手机号后6位'
                except Exception as e:
                    log.error('申请会员失败：' + str(e))
                    status = 400
                    msg = '申请失败！'
        return JsonResponse({'status': status, 'msg': msg})


def change_pwd(request):
    """
    修改密码
    :param request:
    :return:
    """
    if request.method == 'POST':
        mem_id = request.POST.get('mem_id', '')
        old_pwd = request.POST.get('old_pwd', '')
        new_pwd1 = request.POST.get('new_pwd1', '')
        new_pwd2 = request.POST.get('new_pwd2', '')
        if any((not mem_id, not old_pwd, not new_pwd1, not new_pwd2, len(mem_id) == 0, len(new_pwd1) == 0,
                len(new_pwd2) == 0)):
            log.error('密码修改失败：无效的参数')
            msg = '操作失败！'
            status = 400
        else:
            if new_pwd1 != new_pwd2:
                log.error('密码修改失败：两次密码输入不一致！')
                msg = '两次输入的密码不一致！'
                status = 400
            else:
                try:
                    member = Members.objects.get(pk=mem_id)
                    member.auth_str = make_pwd(new_pwd1)
                    member.save()
                    msg = '操作成功！'
                    status = 200
                except Exception as e:
                    log.error('密码修改失败：' + str(e))
                    msg = '操作失败！'
                    status = 400
        return JsonResponse({'status': status, 'msg': msg})


def get_area(request):
    """
    获取所有地址
    :param request:
    :return:
    """
    try:
        areas = AreaAddr.objects.all()
        area_list = []
        for area in areas:
            area_list.append({
                'id': area.id,
                'area': area.area,
                'addr': area.addr
            })
        return JsonResponse({
            'status': 200,
            'msg': '操作成功！',
            'data': {
                'area_list': area_list
            }
        })
    except Exception as e:
        log.error('获取地址失败：' + str(e))
        return JsonResponse({'status': 400, 'msg': '操作失败！'})


def apply_for_qualification(request):
    """
    申请资质
    :param request:
    :return:
    """
    if request.method == 'POST':
        mem_id = request.POST.get('mem_id', '')
        addr_id = request.POST.get('addr_id', '')
        if any((not mem_id, not addr_id, len(mem_id) == 0, len(addr_id) == 0)):
            log.error('申请资质失败：无效的参数')
            msg = '申请失败！'
            status = 400
        else:
            try:
                member = Members.objects.get(pk=mem_id)
                if member.qualification_code == 1:
                    return JsonResponse({'status': 400, 'msg': '您已申请资质，请勿重复申请！'})
                member.area_id = addr_id
                member.qualification_code = 1
                member.save()
                msg = '申请成功！'
                status = 200
            except Exception as e:
                log.error('申请资质失败：' + str(e))
                msg = '申请失败！'
                status = 400
        return JsonResponse({'status': status, 'msg': msg})


def get_qualification(request):
    """
    获取用户资质申请状态
    :param request:
    :return:
    """
    mem_id = request.GET.get('mem_id', '')
    if any((not mem_id, len(mem_id) == 0)):
        log.error('获取用户资质失败：无效的参数')
    else:
        try:
            member = Members.objects.get(pk=mem_id)
            return JsonResponse({
                'status': 200,
                'msg': '查询成功！',
                'data': {
                    'status': member.qualification.name
                }
            })
        except Exception as e:
            log.error('获取用户资质失败：' + str(e))
    return JsonResponse({
        'status': 400,
        'msg': '查询失败！'
    })


def upload_pic(request):
    """
    上传申请资质照片
    :param request:
    :return:
    """
    if request.method == 'POST':
        mem_id = request.POST.get('mem_id', None)
        pic = request.FILES.get('pic', None)
        if any((not pic, not mem_id, len(mem_id) == 0)):
            log.error('照片上传失败：无效的参数')
            msg = '上传失败！'
            status = 400
        else:
            try:
                member_material = MemberMaterials.objects.create(mem_id=mem_id,
                                                                 materials_name='{}_{}'.format(mem_id, pic.name))

                with open(BASE_DIR + '/static/media/pic/{}_{}'.format(mem_id, pic.name), 'wb+') as f:
                    for chunk in pic.chunks():
                        f.write(chunk)
                member_material.save()
                return JsonResponse({
                    'status': 200,
                    'msg': '上传成功！',
                    'data': {
                        'pic_url': '/s/media/pic/{}_{}'.format(mem_id, pic.name)
                    }
                })
            except Exception as e:
                log.error('照片上传失败：' + str(e))
                msg = '上传失败！'
                status = 400
        return JsonResponse({'status': status, 'msg': msg})


def get_compact(request):
    """
    获取所有合同模板
    :param request:
    :return:
    """
    try:
        compact_list = os.listdir(BASE_DIR + '/static/media/compact')
        return JsonResponse({
            'status': 200,
            'msg': '获取成功！',
            'data': {
                'compact_list': compact_list
            }
        })
    except Exception as e:
        log.error('获取模板文件列表失败：' + str(e))
        return JsonResponse({
            'status': 400,
            'msg': '获取失败！'
        })


def download_compact(request):
    """
    下载合同模板
    :param request:
    :return:
    """
    file_name = request.GET.get('file_name', '')
    if any((not file_name, len(file_name) == 0)):
        log.error('下载合同模板失败：无效的文件名')
    else:
        try:
            f = open(BASE_DIR + '/static/media/compact/' + file_name, 'rb')
            response = FileResponse(f)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment;filename="{urllib.parse.quote(file_name)}"'
            return response
        except Exception as e:
            log.error('下载合同模板失败：' + str(e))
    return JsonResponse({
        'status': 400,
        'msg': '下载失败！'
    })
