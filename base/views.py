# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, generics, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from base.authentication import CsrfExemptSessionAuthentication
from base.permissions import *
from base.serializers import *
from base.exceptions import *
import pandas as pd


class SensorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class SetaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Seta.objects.all()
    serializer_class = SetaSerializer

    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class ValueSensorSetaViewSet(mixins.CreateModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    queryset = ValueSensorSeta.objects.all()
    serializer_class = ValueSensorSetaSerializer
    permission_classes = (LocalOrIsAuthenticated,)

    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ('seta__id', 'seta__name', 'sensor__id', 'sensor__name')
    ordering_fields = ('date',)
    ordering = ('-date',)


class MultipleValuesAPIView(generics.GenericAPIView):
    queryset = ValueSensorSeta.objects.none()
    serializer_class = DynamicValueSensorSetaSerializer
    permission_classes = (LocalOrIsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        request._full_data = request.GET
        return self.create(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        pks = []
        response = {
            'created': [],
            'errors': {}
        }
        seta = None
        try:
            seta = Seta.objects.get(pk=kwargs.get('seta_pk'))
            for key in request.data:
                if key == 'csrfmiddlewaretoken':
                    continue
                sensor = seta.sensors.filter(name=key)
                num_sensors = sensor.count()
                if num_sensors == 0:
                    response['errors'][key] = 'Not found'
                    continue
                elif num_sensors > 1:
                    response['errors'][key] = 'Multiples options'
                    continue
                sensor = sensor.get()
                value = request.data[key]

                pks.append(
                    ValueSensorSeta.objects.create(seta=seta, sensor=sensor, value=value).pk
                )
            response_status = status.HTTP_201_CREATED
        except Seta.DoesNotExist:
            response_status = status.HTTP_404_NOT_FOUND

        serializer = ValueSensorSetaSerializer(
            ValueSensorSeta.objects.filter(pk__in=pks),
            many=True, context={'request': request}
        )
        response['created'] = serializer.data
        if not response['created']:
            if seta:
                response_status = status.HTTP_400_BAD_REQUEST
        elif response['errors']:
            response_status = status.HTTP_202_ACCEPTED
        return Response(response, status=response_status)


class BulkAPIView(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  generics.GenericAPIView):
    queryset = BulkData.objects.none()
    parser_classes = (MultiPartParser, )
    permission_classes = (LocalOrIsAuthenticated,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_serializer(self, *args, **kwargs):
        many = kwargs.get('many')
        context = kwargs.get('context')
        if many or context:
            self.serializer_class = BulkDataSerializer
        else:
            self.serializer_class = NewBulkDataSerializer
        return super(BulkAPIView, self).get_serializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        request._full_data = request.GET
        seta_pk = kwargs.get('seta_pk')
        if seta_pk:
            self.queryset = BulkData.objects.filter(seta_id=seta_pk)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        try:
            seta = generics.get_object_or_404(Seta, pk=kwargs.get('seta_pk'))

            f = request.data.get('datos')

            if seta.check_bulk:
                content_type = 'text/plain'
                if hasattr(f, 'content_type'):
                    content_type = f.content_type
                file_data = None
                if content_type in ['text/csv', 'text/plain']:
                    options = {
                        'sep': seta.separator,
                        'decimal': seta.decimal,
                    }
                    if seta.date_parse:
                        options['parse_dates'] = False  # Not used in this point
                        options['date_parser'] = seta.date_parse

                    file_data = pd.read_csv(f, **options)
                elif content_type in [
                    'application/vnd.ms-excel',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                ]:
                    pass  # file_data = pd.read_excel(f) Not supported
                elif content_type == 'application/vnd.oasis.opendocument.spreadsheet':
                    pass  # .ods Not supported

                if file_data is None:
                    raise FileWrongException()
                wrong_columns = []
                has_date = False
                for key in file_data.columns:
                    if key != seta.date_column:
                        if not seta.sensors.filter(name=key).exists():
                            wrong_columns.append(key)
                    else:
                        has_date = True
                if not has_date and seta.date_parse:
                    if wrong_columns:
                        raise FileWrongColumnsException(
                            _('Columns date requited and columns "{columns_name}" have wrong sensor name').format(
                                columns_name=','.join(wrong_columns)
                            )
                        )
                    else:
                        raise FileWrongColumnsException(_('Columns date requited'))

                if wrong_columns:
                    raise FileWrongColumnsException(
                        _('Columns "{columns_name}" have wrong sensor name').format(
                            columns_name=','.join(wrong_columns)
                        )
                    )

            serializer = self.get_serializer(
                BulkData.objects.create(
                    seta=seta,
                    datos=f
                ),
                context={'request': request}
            )
            response_status = status.HTTP_201_CREATED
            return Response(serializer.data, status=response_status)
        except Seta.DoesNotExist:
            response_status = status.HTTP_404_NOT_FOUND
            return Response({'seta': 'Not found'}, status=response_status)
