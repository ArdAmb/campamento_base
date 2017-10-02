# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from base.models import *


class ValueSensorSetaAdmin(admin.ModelAdmin):
    list_filter = ('sensor', 'seta')
    list_display = ('value', 'sensor', 'seta')

admin.site.register(Sensor)
admin.site.register(Seta)
admin.site.register(ValueSensorSeta, ValueSensorSetaAdmin)
admin.site.register(BulkData)
