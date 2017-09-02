# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from base.serializers import *
from base.models import *


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class SetaViewSet(viewsets.ModelViewSet):
    queryset = Seta.objects.all()
    serializer_class = SetaSerializer


class ValueSensorSetaViewSet(viewsets.ModelViewSet):
    queryset = ValueSensorSeta.objects.all()
    serializer_class = ValueSensorSetaSerializer

