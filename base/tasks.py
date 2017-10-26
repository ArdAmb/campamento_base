# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pandas as pd

from base.models import *


def process_bulk(bulk_pk):
    bulk = BulkData.objects.get(pk=bulk_pk)
    seta = bulk.seta
    f = bulk.datos
    options = {
        'sep': seta.separator,
        'decimal': seta.decimal,
    }
    date_pos = None
    if seta.date_parse:
        options['parse_dates'] = True
        options['date_parser'] = seta.date_parse
    file_data = pd.read_csv(f, **options)
    if seta.date_parse:
        date_pos = list(file_data.columns).index(seta.date_column)

    if not (date_pos is None):
        for line in file_data.values:
            entry_date = line[date_pos]
            pos = 0
            for key in file_data.columns:
                if key != seta.date_column:
                    if seta.sensors.filter(name=key).exists():
                        sensor = seta.sensors.get(name=key)
                        ValueSensorSeta.objects.create(
                            seta=seta,
                            sensor=sensor,
                            value=line[pos],
                            date=entry_date
                        )
                pos += 1
    bulk.processed = True
    bulk.save()
