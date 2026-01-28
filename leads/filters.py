import django_filters
from django.utils import timezone
from .models import Lead
from datetime import timedelta


class LeadFilter(django_filters.FilterSet):
    # Filter for exact status
    status = django_filters.CharFilter(lookup_expr='iexact')
    
    # Custom filter: "Leads expiring greater than X days from now"
    days_until_expiry_gt = django_filters.NumberFilter(method='filter_expiry_gt')
    
    # Standard Date Range filters
    min_value = django_filters.NumberFilter(field_name="value", lookup_expr='gte')
    max_value = django_filters.NumberFilter(field_name="value", lookup_expr='lte')

    class Meta:
        model = Lead
        fields = ['status', 'source']

    def filter_expiry_gt(self, queryset, name, value):
        """
        Calculates the date X days from now and finds leads 
        with closure date AFTER that.
        """
        try:
            days = int(value)
            target_date = timezone.now().date() + timedelta(days=days)
            return queryset.filter(expected_closure_date__gt=target_date)
        except ValueError:
            return queryset

