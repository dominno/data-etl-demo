import pathlib
import tempfile

from datetime import date

from django.test import TestCase
from django.urls import reverse

from metrics.data_importer import Importer
from metrics.models import Metric, Campaign, Datasource


class ImporterTestCase(TestCase):

    def setUp(self):
        fixture = """
        Date,Datasource,Campaign,Clicks,Impressions
01.01.2019,test source 1,test campaign 1,10,100
20.01.2019,test source 2,test campaign 2,10,100
22.01.2019,test source 3,test campaign 3,,
        """
        self.importer = Importer(data_source=self.get_temp_file_uri(fixture))
        self.importer.run()

    def test_metric_data_should_be_created(self):
        self.assertTrue(Metric.objects.exists())

    def test_campaign_should_be_created(self):
        self.assertTrue(Campaign.objects.exists())

    def test_datasource_should_be_created(self):
        self.assertTrue(Datasource.objects.exists())

    def test_empty_metric_should_be_filled_with_zero(self):
        metric = Metric.objects.last()
        self.assertEqual(metric.clicks, 0)
        self.assertEqual(metric.impressions, 0)

    def get_temp_file_uri(self, fixture):
        outfile_path = tempfile.mkstemp()[1]
        with open(outfile_path, 'w') as outfile:
            outfile.write(fixture)

        return pathlib.Path(outfile_path).as_uri()


class ViewTestCase(TestCase):

    def setUp(self):
        self.campaign = Campaign.objects.create(name='test campaign')
        self.datasource = Datasource.objects.create(name='test datasource')
        Metric.objects.create(date=date(2020, 1, 1), campaign=self.campaign, datasource=self.datasource, clicks=10, impressions=100)
        Metric.objects.create(date=date(2020, 1, 10), campaign=self.campaign, datasource=self.datasource, clicks=20, impressions=200)

    def test_dashboard_should_return_200_code(self):
        response = self.client.get(reverse('metrics:dashboard'))

        self.assertEqual(response.status_code, 200)

    def test_should_be_able_to_get_json_data_points(self):
        response = self.client.get(reverse('metrics:data_json'))

        self.assertEqual(response.status_code, 200)

        expected = {
            'clicks': [
                {'x': '2020-01-01T00:00:00', 'y': 10},
                {'x': '2020-01-02T00:00:00', 'y': 0},
                {'x': '2020-01-03T00:00:00', 'y': 0},
                {'x': '2020-01-04T00:00:00', 'y': 0},
                {'x': '2020-01-05T00:00:00', 'y': 0},
                {'x': '2020-01-06T00:00:00', 'y': 0},
                {'x': '2020-01-07T00:00:00', 'y': 0},
                {'x': '2020-01-08T00:00:00', 'y': 0},
                {'x': '2020-01-09T00:00:00', 'y': 0},
                {'x': '2020-01-10T00:00:00', 'y': 20}
            ],
            'impressions': [
                {'x': '2020-01-01T00:00:00', 'y': 100},
                {'x': '2020-01-02T00:00:00', 'y': 0},
                {'x': '2020-01-03T00:00:00', 'y': 0},
                {'x': '2020-01-04T00:00:00', 'y': 0},
                {'x': '2020-01-05T00:00:00', 'y': 0},
                {'x': '2020-01-06T00:00:00', 'y': 0},
                {'x': '2020-01-07T00:00:00', 'y': 0},
                {'x': '2020-01-08T00:00:00', 'y': 0},
                {'x': '2020-01-09T00:00:00', 'y': 0},
                {'x': '2020-01-10T00:00:00', 'y': 200},
            ]
        }

        self.assertEqual(response.json()['clicks'], expected['clicks'])
        self.assertEqual(response.json()['impressions'], expected['impressions'])

    def test_should_be_filter_by_date(self):
        Metric.objects.create(date=date(2020, 1, 2), campaign=self.campaign, datasource=self.datasource, clicks=20,
                              impressions=200)
        Metric.objects.create(date=date(2020, 1, 5), campaign=self.campaign, datasource=self.datasource, clicks=20,
                              impressions=200)
        Metric.objects.create(date=date(2020, 1, 6), campaign=self.campaign, datasource=self.datasource, clicks=20,
                              impressions=200)
        response = self.client.get(reverse('metrics:data_json')+"?start_date=2020-01-02&end_date=2020-01-05")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['clicks'],
                         [{'x': '2020-01-02T00:00:00', 'y': 20}, {'x': '2020-01-03T00:00:00', 'y': 0},
                          {'x': '2020-01-04T00:00:00', 'y': 0}, {'x': '2020-01-05T00:00:00', 'y': 20}])
        self.assertEqual(response.json()['impressions'],
                         [{'x': '2020-01-02T00:00:00', 'y': 200}, {'x': '2020-01-03T00:00:00', 'y': 0},
                          {'x': '2020-01-04T00:00:00', 'y': 0}, {'x': '2020-01-05T00:00:00', 'y': 200}])
