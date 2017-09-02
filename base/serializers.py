# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from base.models import *


class SensorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sensor
        fields = ('name', 'sensor_type')


class SetaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Seta
        fields = ('name', 'sensors')


class ValueSensorSetaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ValueSensorSeta
        fields = ('seta', 'sensor', 'value')
