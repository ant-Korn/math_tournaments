# -*- coding: utf-8 -*-
# Generated by Django 1.11b1 on 2017-09-27 19:53
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

def add_permissions_to_group(apps, shema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    group, created = Group.objects.get_or_create(name='tour_editors')
    permissions = Permission.objects.filter(codename__in = [
        'add_tournament',
        'change_tournament',
        'delete_tournament',
        'add_round',
        'change_round',
        'delete_round',
        'add_task',
        'change_task',
        'delete_task',
    ])
    group.permissions.add(*permissions)
    group.save()

class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
            migrations.RunPython(add_permissions_to_group)
    ]
