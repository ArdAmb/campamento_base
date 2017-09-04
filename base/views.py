# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.filters import OrderingFilter, SearchFilter
from base.serializers import *
from base.permissions import *
from base.models import *


class SensorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

    filter_backends = (SearchFilter, )
    search_fields = ('name', )


class SetaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Seta.objects.all()
    serializer_class = SetaSerializer

    filter_backends = (SearchFilter, )
    search_fields = ('name', )


class ValueSensorSetaViewSet(mixins.CreateModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    queryset = ValueSensorSeta.objects.all()
    serializer_class = ValueSensorSetaSerializer
    permission_classes = (LocalOrIsAuthenticated,)

    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ('seta__id', 'seta__name', 'sensor__id', 'sensor__name')
    ordering_fields = ('date', )
    ordering = ('-date', )
