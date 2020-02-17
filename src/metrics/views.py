import datetime

from django.shortcuts import render
from django.views.generic.base import View
from django.http import JsonResponse
from django.db.models import Sum
from django.conf import settings

from metrics.forms import MetricFilterForm
from metrics.models import Metric, Datasource, Campaign


class DashBoardView(View):
    def get(self, request):
        form = MetricFilterForm()
        return render(request, 'metrics/dashboard.html', {'form': form})


def metrics_data_json(request):
    campaigns_ids = request.GET.getlist('campaigns')
    datasources_ids = request.GET.getlist('datasources')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    result = {}
    query_filters = {}

    if not (start_date and end_date):
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(weeks=settings.DEFAULT_WEEKS_IN_THE_PAST)

    query_filters.update(dict(date__gte=start_date, date__lte=end_date))

    if datasources_ids:
        query_filters.update(dict(datasource__id__in=datasources_ids))
        datasources = Datasource.objects.filter(id__in=datasources_ids).values_list('name', flat=True)
        result['title'] = "Datasource: %s." % " and ".join(datasources)
    else:
        result['title'] = "Datasource: All datasources."

    if campaigns_ids:
        query_filters.update(dict(campaign__id__in=campaigns_ids))
        campaigns = Campaign.objects.filter(id__in=campaigns_ids).values_list('name', flat=True)
        result['title'] += ";Campaign: %s." % " and ".join(campaigns)
    else:
        result['title'] += ";Campaign: All campaigns."

    metrics = Metric.objects.filter(**query_filters)\
        .values('date').annotate(clicks=Sum('clicks'), impressions=Sum('impressions'))\
        .order_by('date')

    result.update(get_data_points(metrics))
    result['date_range'] = "%s - %s" % (start_date, end_date)
    return JsonResponse(result)


def get_data_points(metrics):
    result = {}
    for label in ["Clicks", "Impressions"]:
        label_lower = label.lower()
        label_ts = metrics.to_timeseries(index='date', fieldnames=['date', label_lower]).asfreq('D', fill_value=0)
        data = []
        for timestamp, value in getattr(label_ts, label_lower).items():
            data.append({
                'x': timestamp.to_pydatetime().isoformat(),
                'y': value,
            })
        result[label.lower()] = data

    return result
