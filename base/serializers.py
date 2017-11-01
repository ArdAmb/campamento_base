# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.utils.translation import ugettext as _
from rest_framework import serializers
#from rest_framework.exceptions import ValidationError

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
        serializers.HyperlinkedModelSerializer.is_valid(self, raise_exception=raise_exception)

        sensor = self.validated_data['sensor']
        sensores = None
        num_sensores = 0
        if sensor:
            sensores = Sensor.objects.filter(**sensor)
            num_sensores = sensores.count()
            if num_sensores == 1:
                self.fields['sensor'].instance = sensores.get()

        seta = self.validated_data['seta']
        setas = None
        num_setas = 0
        if seta:
            setas = Seta.objects.filter(**seta)
            num_setas = setas.count()
            if num_setas == 1:
                self.fields['seta'].instance = setas.get()

        if setas is not None:
            if num_setas > 1:
                self._errors['seta'] = _('Multiples options')
            elif num_setas == 0:
                self._errors['seta'] = _('Not found')
        if sensores is not None:
            if num_sensores > 1:
                self._errors['sensor'] = _('Multiples options')
            elif num_sensores == 0:
                self._errors['sensor'] = _('Not found')

        seta = self.fields['seta'].instance
        sensor = self.fields['sensor'].instance
        if seta and sensor:
            has_sensor = seta.sensors.filter(pk=sensor.pk)
            if not has_sensor.exists():
                self._errors['seta'] = _('Sensor "{}" not supported').format(sensor.name)
                logger.error('Sensor "{}" not supported for {}'.format(sensor.name, seta.name))

            self.validated_data['seta'] = self.fields['seta'].instance
            self.validated_data['sensor'] = self.fields['sensor'].instance

        if seta and seta.check_value and sensor.sensor_type != TYPE_STRING:
            value = self.validated_data['value']
            try:
                if sensor.sensor_type == TYPE_INT:
                    int(value)
                elif sensor.sensor_type == TYPE_FLOAT:
                    float(value)
            except (ValueError, TypeError):
                error_text = _('Sensor "{}" not support the data "{}"').format(sensor.name, value)
                self._errors['value'] = error_text
                logger.error(error_text)

        if self._errors and raise_exception:
            raise serializers.ValidationError(self.errors)

        return not bool(self._errors)


class BulkDataSerializer(serializers.ModelSerializer):
    datos = serializers.CharField()

    class Meta:
        model = BulkData
        exclude = ('seta', )


class NewBulkDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkData
        fields = ('datos', )
