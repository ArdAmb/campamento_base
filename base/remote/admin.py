# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from base.remote.models import *


class RemoteChatAdmin(admin.ModelAdmin):
    list_filter = ('chat_type',)
    list_display = ('name', 'chat_type')


admin.site.register(RemoteChat, RemoteChatAdmin)
