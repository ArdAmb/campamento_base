# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext as _

from base.models import *


class ValueSensorSetaAdmin(admin.ModelAdmin):
    list_filter = ('sensor', 'seta')
    list_display = ('value', 'sensor', 'seta')


class SetaAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    list_filter = ('check_bulk', )

    fieldsets = (
        (None, {
            'fields': ('name', 'sensors')
        }),
        (_('Bulk'), {
            'classes': ('collapse',),
            'fields': ('check_bulk', 'separator', 'date_parse', 'date_column', 'decimal'),
        }),
    )


admin.site.register(Sensor)
admin.site.register(Seta, SetaAdmin)
admin.site.register(ValueSensorSeta, ValueSensorSetaAdmin)
admin.site.register(BulkData)
