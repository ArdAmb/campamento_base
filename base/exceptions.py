# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework.exceptions import APIException
from django.utils.translation import ugettext as _


class FileWrongException(APIException):
    status_code = 409
    default_detail = _('The file have wrong format')
    default_code = 'file_wrong_format'


class FileWrongColumnsException(APIException):
    status_code = 409
    default_detail = _('The file contains wrong data, check the columns')
    default_code = 'file_wrong_columns'
