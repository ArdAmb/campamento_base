# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework import routers

from base.views import *

router = routers.SimpleRouter()
router.register(r'sensor', SensorViewSet)
router.register(r'seta', SetaViewSet)
router.register(r'value', ValueSensorSetaViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^bulk/(?P<seta_pk>[^/.]+)/$', BulkValuesAPIView.as_view()),
]
