import sys
import traceback

import pandas
import datetime

from django.conf import settings

from metrics.models import Datasource, Campaign, Metric


def datasource_converter(value):
    return _value_to_model_id(value, Datasource)


def campaign_converter(value):
    return _value_to_model_id(value, Campaign)


def _value_to_model_id(value, ModelClass):
    instance, created = ModelClass.objects.get_or_create(name=value.lower())
    return instance.pk


class Importer():

    def __init__(self, data_source=None, chunk_size=1000):
        if not data_source:
            data_source = settings.ETL_CSV_URL

        self.data_source = data_source
        self.chunksize = chunk_size

    def run(self):
        try:
            data_chunks = self.read_data()
            self.store(data_chunks)
        except:
            print('Error while storing or reading data')
            traceback.print_exc(file=sys.stdout)

    def read_data(self):
        converters = {
            'Datasource': datasource_converter,
            'Campaign': campaign_converter,
            'Impressions': lambda x: int(x) if x else 0,
            'Clicks': lambda x: int(x) if x else 0,
        }
        return pandas.read_csv(
            self.data_source,
            iterator=True,
            chunksize=self.chunksize,
            converters=converters,
            parse_dates=[0],
            date_parser=lambda dates: [datetime.datetime.strptime(value, '%d.%m.%Y') for value in dates]
        )

    def store(self, data_chunks):
        for chunk in data_chunks:
            chunk.columns = ['date', 'datasource_id', 'campaign_id', 'clicks', 'impressions']
            objs = (Metric(**row) for df_index, row in chunk.iterrows())
            Metric.objects.bulk_create(objs)
