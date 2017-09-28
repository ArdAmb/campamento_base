# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from base.models import *

logger = logging.getLogger(__name__)


class SensorNameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sensor
        fields = ('name', 'url')


class SensorSerializer(serializers.HyperlinkedModelSerializer):
    sensor_type = serializers.SerializerMethodField()

    class Meta:
        model = Sensor
        fields = '__all__'

    def get_sensor_type(self, obj):
        return obj.get_sensor_type_display()


class SetaNameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Seta
        fields = ('name', 'url')


class SetaSerializer(serializers.HyperlinkedModelSerializer):
    sensors = SensorNameSerializer(read_only=True, many=True)

    class Meta:
        model = Seta
        fields = '__all__'


class DynamicValueSensorSetaSerializer(serializers.HyperlinkedModelSerializer):
    sensor_name = serializers.CharField(source='sensor.name',
                                        help_text='Field with name of the sensor and values for this sensor',
                                        style={'template': 'campamento/dynamic-input.html'})

    class Meta:
        model = ValueSensorSeta
        fields = ('id', 'sensor_name')


class ValueSensorSetaSerializer(serializers.HyperlinkedModelSerializer):
    sensor = SensorNameSerializer()
    seta = SetaNameSerializer()
    date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ValueSensorSeta
        fields = '__all__'

    def is_valid(self, raise_exception=False):
        sensor = self.initial_data.get('sensor')
        sensores = None
        num_sensores = 0
        if sensor:
            sensores = Sensor.objects.filter(**sensor)
            num_sensores = sensores.count()
            if num_sensores == 1:
                self.fields['sensor'].instance = sensores.get()

        seta = self.initial_data.get('seta')
        setas = None
        num_setas = 0
        if seta:
            setas = Seta.objects.filter(**seta)
            num_setas = setas.count()
            if num_setas == 1:
                self.fields['seta'].instance = setas.get()

        try:
            serializers.HyperlinkedModelSerializer.is_valid(self, raise_exception=raise_exception)
        except ValidationError, ex:
            if hasattr(ex, 'detail'):
                if ex.detail.get('seta') and setas is not None:
                    if num_setas > 1:
                        ex.detail['seta'] = [_('Multiples options')]
                    elif num_setas == 0:
                        ex.detail['seta'] = [_('Not found')]
                if ex.detail.get('sensor') and sensores is not None:
                    if num_sensores > 1:
                        ex.detail['sensor'] = [_('Multiples options')]
                    elif num_sensores == 0:
                        ex.detail['sensor'] = [_('Not found')]
            raise ex

        seta = self.fields['seta'].instance
        sensor = self.fields['sensor'].instance
        if seta and sensor:
            has_sensor = seta.sensors.filter(pk=sensor.pk)
            if not has_sensor.exists():
                self._errors = {'seta': [_('Sensor "{}" not supported').format(sensor.name)]}
                logger.error('Sensor "{}" not supported for {}'.format(sensor.name, seta.name))

            self.validated_data['seta'] = self.fields['seta'].instance
            self.validated_data['sensor'] = self.fields['sensor'].instance

        # TODO debemos validar el valor segun el dato o es mejor guardarlo?

        if self._errors and raise_exception:
            raise ValidationError(self.errors)

        return not bool(self._errors)
