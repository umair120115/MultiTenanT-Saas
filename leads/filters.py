# import django_filters
# from django.utils import timezone
# from .models import Lead
# from datetime import timedelta


# class LeadFilter(django_filters.FilterSet):
#     # Filter for exact status
#     status = django_filters.CharFilter(lookup_expr='iexact')
    
#     # Custom filter: "Leads expiring greater than X days from now"
#     days_until_expiry_gt = django_filters.NumberFilter(method='filter_expiry_gt')
    
#     # Standard Date Range filters
#     min_value = django_filters.NumberFilter(field_name="value", lookup_expr='gte')
#     max_value = django_filters.NumberFilter(field_name="value", lookup_expr='lte')

#     class Meta:
#         model = Lead
#         fields = ['status', 'source']

#     def filter_expiry_gt(self, queryset, name, value):
#         """
#         Calculates the date X days from now and finds leads 
#         with closure date AFTER that.
#         """
#         try:
#             days = int(value)
#             target_date = timezone.now().date() + timedelta(days=days)
#             return queryset.filter(expected_closure_date__gt=target_date)
#         except ValueError:
#             return queryset



import django_filters
from django.db.models import Count, Q
from django.utils import timezone
from .models import Lead
from datetime import timedelta

class LeadFilter(django_filters.FilterSet):
    # --- Existing Filters ---
    status = django_filters.CharFilter(lookup_expr='iexact')
    days_until_expiry_gt = django_filters.NumberFilter(method='filter_expiry_gt')
    min_value = django_filters.NumberFilter(field_name="value", lookup_expr='gte')
    max_value = django_filters.NumberFilter(field_name="value", lookup_expr='lte')

    # --- NEW: Duplicate Filter ---
    # When set to true (?show_duplicates=true), it filters the list to show 
    # only leads that have a duplicate email OR contact number.
    show_duplicates = django_filters.BooleanFilter(
        method='filter_duplicates', 
        label="Show Duplicates Only"
    )

    class Meta:
        model = Lead
        fields = ['status', 'source']

    def filter_expiry_gt(self, queryset, name, value):
        try:
            days = int(value)
            target_date = timezone.now().date() + timedelta(days=days)
            return queryset.filter(expected_closure_date__gt=target_date)
        except ValueError:
            return queryset

    def filter_duplicates(self, queryset, name, value):
        """
        Filters the queryset to show ONLY records that share an email 
        or contact_number with another record in the current list.
        """
        if value:
            # 1. Find emails that appear more than once in the current set
            dup_emails = (
                queryset.values('email')
                .annotate(count=Count('id'))
                .filter(count__gt=1)
                .values_list('email', flat=True)
            )
            
            # 2. Find contact numbers that appear more than once
            dup_phones = (
                queryset.values('contact_number')
                .annotate(count=Count('id'))
                .filter(count__gt=1)
                .values_list('contact_number', flat=True)
            )
            
            # 3. Filter the main queryset to return rows matching those duplicates
            return queryset.filter(
                Q(email__in=dup_emails) | Q(contact_number__in=dup_phones)
            )
        
        return queryset