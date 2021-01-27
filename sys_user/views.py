import os
import urllib

from PIL import Image

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect

from common import make_pwd, BASE_URL, BASE_DIR
from log_util import log
from sys_user.models import SysUser, AreaAddr, Members, MemberMaterials


def to_login(request):
    """
    跳转到登录页
    :param request:
    :return:
    """
    if request.method == 'POST':
        # 获取用户名和口令
        name = request.POST.get('username', '')
        pwd = request.POST.get('password', '')

        if any((not name, not pwd, len(name) == 0, len(pwd) == 0)):
            error = '用户名或口令不能为空！'
        else:
            ret = SysUser.objects.filter(name=name, auth_str=make_pwd(pwd))
            if ret.exists():
                login_user = ret.first()

                # 将登陆的用户信息存在session中
                request.session['login_sys_user'] = {
                    'id': login_user.id,
                    'name': login_user.name
                }

                return redirect('/sys/')

            error = '用户名或口令错误！'

    return render(request, 'sys_user/login.html', locals())


def to_logout(request):
    """
    登出
    :param request:
    :return:
    """
    request.session.pop('login_sys_user')
    return redirect('/sys/login/')


def to_area_mgr(request):
    """
    查询地址
    :param request:
    :return:
    """
    try:
        areas = AreaAddr.objects.all().order_by('id')

        paginator = Paginator(areas, 8, 0)
        page_num = request.GET.get('page_num', '')
        if page_num:
            if int(page_num) <= paginator.num_pages:
                page = paginator.page(page_num)
            else:
                page = paginator.page(paginator.num_pages)
        else:
            page = paginator.page(1)
        return render(request, 'sys_user/area_mgr.html', {'page': page, 'paginator': paginator})
    except Exception as e:
        log.error('地址查询失败：' + str(e))


def add_addr(request):
    """
    添加地址
    :param request:
    :return:
    """
    if request.method == 'POST':
        area = request.POST.get('area', '')
        addr = request.POST.get('addr', '')
        if any((not area, not addr, len(area) == 0, len(addr) == 0)):
            msg = '区域或详细地址不能为空！'
            status = 400
        else:
            try:
                AreaAddr.objects.create(area=area, addr=addr)
                msg = '添加成功'
                status = 200
            except Exception as e:
                log.error('地址添加失败：' + str(e))
                msg = '地址添加失败！'
                status = 400
        return JsonResponse({'status': status, 'msg': msg})


def edit_addr(request):
    """
    修改地址
    :param request:
    :return:
    """
    if request.method == 'POST':
        addr_id = request.POST.get('id', '')
        area = request.POST.get('area', '')
        addr = request.POST.get('addr', '')
        print(addr_id, type(area), type(addr))
        if any((not addr_id, not area, not addr, len(addr_id) == 0, len(area) == 0, len(addr) == 0)):
            msg = '区域或详细地址不能为空！'
            status = 400
        else:
            try:
                area_addr = AreaAddr.objects.get(pk=addr_id)
                area_addr.area, area_addr.addr = area, addr
                area_addr.save()
                msg = '地址修改成功！'
                status = 200
            except Exception as e:
                log.error('地址修改失败：' + str(e))
                msg = '地址修改失败！'
                status = 400
        return JsonResponse({'status': status, 'msg': msg})


def delete_addr(request):
    """
    删除地址
    :param request:
    :return:
    """
    addr_id = request.GET.get('id', '')
    if any((not addr_id, len(addr_id) == 0)):
        log.error('地址删除失败：无效的id')
        msg = '删除失败！'
        status = 400
    else:
        try:
            addr = AreaAddr.objects.get(pk=addr_id)
            addr.delete()
            msg = '删除成功！'
            status = 200
        except Exception as e:
            log.error('地址删除失败：' + str(e))
            msg = '删除失败！'
            status = 400
    return JsonResponse({'status': status, 'msg': msg})


def all_mem_apply_for(request):
    """
    获取所有申请资质的客户
    :param request:
    :return:
    """
    try:
        members = Members.objects.filter(qualification_code=1).order_by('-id')
        paginator = Paginator(members, 8, 0)
        page_num = request.GET.get('page_num', '')
        if page_num:
            if int(page_num) <= paginator.num_pages:
                page = paginator.page(page_num)
            else:
                page = paginator.page(paginator.num_pages)
        else:
            page = paginator.page(1)
        return render(request, 'sys_user/mem_apply_for_mgr.html', {'page': page, 'paginator': paginator})
    except Exception as e:
        log.error('查询所有资质待审核客户失败：' + str(e))


def get_mem_materials(request):
    """
    获取用户上传的图片
    :param request:
    :return:
    """
    mem_id = request.GET.get('id', '')
    if any((not mem_id, len(mem_id) == 0)):
        log.error('获取用户上传的图片失败：无效的用户id')
        msg = '获取用户上传图片失败！'
        status = 400
    else:
        try:
            materials = MemberMaterials.objects.filter(mem_id=mem_id)
            pic_list = []
            for material in materials:
                pic_list.append(os.path.join(BASE_URL, 's/media/pic/') + material.materials_name)
            return JsonResponse({'status': 200, 'pic_list': pic_list})
        except Exception as e:
            log.error('获取用户上传的图片失败：' + str(e))
            msg = '获取用户上传图片失败！'
            status = 400
    return JsonResponse({'status': status, 'msg': msg})


def rotate_pic(request):
    """
    旋转图片
    :param request:
    :return:
    """
    pic_url = request.GET.get('pic_url', '')
    if any((not pic_url, len(pic_url) == 0)):
        log.error('旋转图片失败：无效的文件名')
        msg = '操作失败！'
        status = 400
    else:
        try:
            pic_name = pic_url.split('/')[-1]
            im = Image.open(os.path.join(BASE_DIR, 'static/media/pic/') + pic_name)
            out = im.transpose(Image.ROTATE_270)
            out.save(os.path.join(BASE_DIR, 'static/media/pic/') + pic_name)
            msg = '操作成功！'
            status = 200
        except Exception as e:
            log.error('旋转图片失败：' + str(e))
            msg = '操作失败！'
            status = 400
    return JsonResponse({'status': status, 'msg': msg})


def change_mem_status(request):
    """
    修改用户审批状态
    :param request:
    :return:
    """
    if request.method == 'POST':
        mem_id = request.POST.get('id', '')
        code = request.POST.get('code', '')
        if any((not mem_id, not code, len(mem_id) == 0, len(code) == 0)):
            log.error('修改客户资质失败：无效的用户id')
            msg = '操作失败！'
            status = 400
        else:
            try:
                member = Members.objects.get(pk=mem_id)
                member.qualification_code = code
                member.save()
                msg = '操作成功！'
                status = 200
            except Exception as e:
                log.error('修改客户资质失败：' + str(e))
                msg = '操作失败！'
                status = 400
        return JsonResponse({'status': status, 'msg': msg})


def search_mem_qualification(request):
    """
    查询客户资质
    :param request:
    :return:
    """
    key = request.GET.get('key', '')
    members = []
    if key:
        try:
            areas = AreaAddr.objects.filter(Q(area__contains=key) | Q(addr__contains=key))
            areas_id = [area.id for area in areas]
            members = Members.objects.filter(Q(name__contains=key) | Q(phone=key) | Q(area_id__in=areas_id)) \
                .order_by('-id')
            print('查询结果', members)
        except Exception as e:
            log.error('查询客户资质失败：' + str(e))
    else:
        try:
            members = Members.objects.all().order_by('-id')
        except Exception as e:
            log.error('查询客户资质失败：' + str(e))
    paginator = Paginator(members, 8, 0)
    page_num = request.GET.get('page_num', '')
    if page_num:
        if int(page_num) <= paginator.num_pages:
            page = paginator.page(page_num)
        else:
            page = paginator.page(paginator.num_pages)
    else:
        page = paginator.page(1)
    return render(request, 'sys_user/mem_qualification_search.html', {'page': page, 'paginator': paginator, 'key': key})


def upload_compact(request):
    """
    上传合同模板
    :param request:
    :return:
    """
    if request.method == 'POST':
        compact = request.FILES.get('compact', None)
        if not compact:
            log.error('合同模板上传失败：没有上传文件')
            msg = '请先选择要上传的文件！'
            status = 400
        else:
            try:
                with open(BASE_DIR + '/static/media/compact/' + compact.name, 'wb+') as f:
                    for chunk in compact.chunks():
                        f.write(chunk)
                msg = '上传成功！'
                status = 200
            except Exception as e:
                log.error('合同模板上传失败：' + str(e))
                msg = '上传失败！'
                status = 400
        return JsonResponse({'status': status, 'msg': msg})


def delete_compact(request):
    """
    删除合同模板
    :param request:
    :return:
    """
    file_name = request.GET.get('file_name', '')
    if any((not file_name, len(file_name) == 0)):
        log.error('合同模板删除失败：无效的文件名！')
        msg = '删除失败！'
        status = 400
    else:
        try:
            os.remove(BASE_DIR + '/static/media/compact/' + file_name)
            msg = '删除成功！'
            status = 200
        except Exception as e:
            log.error('合同模板删除失败：' + str(e))
            msg = '删除失败！'
            status = 200
    return JsonResponse({'status': status, 'msg': msg})


def compact_mgr(request):
    """
    获取所用合同模板
    :param request:
    :return:
    """
    try:
        compact_list = os.listdir(BASE_DIR + '/static/media/compact')
        paginator = Paginator(compact_list, 8, 0)
        page_num = request.GET.get('page_num', '')
        if page_num:
            if int(page_num) <= paginator.num_pages:
                page = paginator.page(page_num)
            else:
                page = paginator.page(paginator.num_pages)
        else:
            page = paginator.page(1)
        return render(request, 'sys_user/compact_mgr.html', {'page': page, 'paginator': paginator})
    except Exception as e:
        log.error('获取模板文件列表失败：' + str(e))


def download_compact(request):
    """
    下载合同模板
    :param request:
    :return:
    """
    file_name = request.GET.get('file_name', '')
    if any((not file_name, len(file_name) == 0)):
        log.error('下载合同模板失败：无效的文件名')
    try:
        f = open(BASE_DIR + '/static/media/compact/' + file_name, 'rb')
        response = FileResponse(f)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment;filename="{urllib.parse.quote(file_name)}"'
        return response
    except Exception as e:
        log.error('下载合同模板失败：' + str(e))


def get_initiation_mem(request):
    """
    获取所有申请入会的会员
    :param request:
    :return:
    """
    try:
        members = Members.objects.filter(activate=0).order_by('-id')
        paginator = Paginator(members, 8, 0)
        page_num = request.GET.get('page_num', '')
        if page_num:
            if int(page_num) <= paginator.num_pages:
                page = paginator.page(page_num)
            else:
                page = paginator.page(paginator.num_pages)
        else:
            page = paginator.page(1)
        return render(request, 'sys_user/mem_join_mgr.html', {'page': page, 'paginator': paginator})
    except Exception as e:
        log.error('获取所有申请入会会员失败：' + str(e))


def activate_member(request):
    """
    批准用户会员申请
    :param request:
    :return:
    """
    mem_id = request.GET.get('id', '')
    code = request.GET.get('code', '')
    if any((not mem_id, not code, len(mem_id) == 0, len(code) == 0)):
        log.error('会员激活失败：参数不能为空！')
        msg = '操作失败！'
        status = 400
    else:
        try:
            member = Members.objects.get(pk=mem_id)
            member.activate = code
            member.save()
            msg = '操作成功！'
            status = 200
        except Exception as e:
            log.error('会员激活失败：' + str(e))
            msg = '操作失败！'
            status = 200
    return JsonResponse({'status': status, 'msg': msg})
