# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AreaAddr(models.Model):
    area = models.CharField(max_length=30)
    addr = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'area_addr'


class MemberMaterials(models.Model):
    mem_id = models.IntegerField()
    materials_name = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'member_materials'


class Qualification(models.Model):
    name = models.CharField(unique=True, max_length=20)
    code = models.IntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'qualification'


class SysUser(models.Model):
    name = models.CharField(unique=True, max_length=50)
    auth_str = models.CharField(max_length=100)
    phone = models.CharField(unique=True, max_length=20)

    class Meta:
        managed = False
        db_table = 'sys_user'


class Members(models.Model):
    name = models.CharField(max_length=50)
    auth_str = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    area_id = models.IntegerField()
    activate = models.IntegerField(default=0)
    qualification_code = models.IntegerField(default=0)

    @property
    def qualification(self):
        return Qualification.objects.get(code=self.qualification_code)

    @property
    def register_area(self):
        area_addr = AreaAddr.objects.get(id=self.area_id)
        return area_addr.area + area_addr.addr

    class Meta:
        managed = False
        db_table = 'members'
