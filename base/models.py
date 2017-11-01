# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _

TYPE_INT = 0
TYPE_FLOAT = 1
TYPE_STRING = 2

TYPE_CHOICES = (
    (TYPE_INT, _('Integer')),
    (TYPE_FLOAT, _('Float')),
    (TYPE_STRING, _('String')),
)


class Sensor(models.Model):
    name = models.CharField(max_length=512)
    sensor_type = models.IntegerField(choices=TYPE_CHOICES, default=TYPE_STRING)

    def __str__(self):
        return self.name


class Seta(models.Model):
    name = models.CharField(max_length=512)
    sensors = models.ManyToManyField(Sensor)

    check_value = models.BooleanField(
        default=False,
        help_text=_('Check the value stored for the sensors (you could lost information)')
    )

    check_bulk = models.BooleanField(
        default=False,
        help_text=_('Check the columns when bulk file is uploaded (you could lost information)')
    )
    separator = models.CharField(
        max_length=1,
        default=';',
        help_text=_('Separator used into the bulk file, for CSV')
    )
    date_parse = models.CharField(
        max_length=16,
        default='',
        blank=True,
        help_text=_('Date format used into the bulk file, for CSV (required for parse the file)')
    )
    date_column = models.CharField(
        max_length=32,
        default='date',
        help_text=_('Date name column used into the bulk file, for CSV')
    )
    decimal = models.CharField(
        max_length=1,
        default=',',
        help_text=_('Decimal separator used into the bulk file, for CSV')
    )

    def __str__(self):
        return self.name


class ValueSensorSeta(models.Model):
    seta = models.ForeignKey(Seta)
    sensor = models.ForeignKey(Sensor)
    value = models.CharField(max_length=512)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return self.value

    def clean(self):
        if not self.seta.sensors.filter(pk=self.sensor.id).exists():
            raise ValidationError(
                _('%(sensor)s is not valid for %(seta)s'),
                params={'sensor': self.sensor, 'seta': self.seta},
            )
        if self.sensor.sensor_type == TYPE_INT:
            try:
                return int(self.value)
            except:
                raise ValidationError(
                    _('%(value)s is not a integer'),
                    params={'value': self.value},
                )
        elif self.sensor.sensor_type == TYPE_FLOAT:
            try:
                return float(self.value)
            except:
                raise ValidationError(
                    _('%(value)s is not a float'),
                    params={'value': self.value},
                )

    def get_value(self):
        if self.sensor.sensor_type == TYPE_INT:
            return int(self.value)
        elif self.sensor.sensor_type == TYPE_FLOAT:
            return float(self.value)
        return self.value


class BulkData(models.Model):
    seta = models.ForeignKey(Seta)
    datos = models.FileField()
    date = models.DateTimeField(auto_now=True)
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return "Bulk data {} for {}".format(self.pk, self.seta)
