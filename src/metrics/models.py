from django.db import models
from django_pandas.managers import DataFrameManager


class Campaign(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "%s" % self.name


class Datasource(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "%s" % self.name


class Metric(models.Model):
    date = models.DateField()
    clicks = models.IntegerField()
    impressions = models.IntegerField()
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    datasource = models.ForeignKey(Datasource, on_delete=models.CASCADE)

    objects = DataFrameManager()


