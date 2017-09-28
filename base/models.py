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
